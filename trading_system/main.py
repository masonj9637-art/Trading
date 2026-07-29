import asyncio
import pandas as pd
import requests
import os
import redis
from execution.alpaca_client import AlpacaTradingClient
from execution.order_manager import OrderManager
from data.alpaca_fetcher import AlpacaDataFetcher
from signals.temporal_alignment import TemporalAligner
from signals.pca_orthogonalization import PCAOrthogonalizer
from signals.smoothing import EMASmoother
from signals.alpha_isolation import AlphaIsolator
from signals.ranking import PortfolioRanker
from core.ensemble_agent import EnsembleAgent
from signals.volatility_guard import VolatilityGuard
from signals.regime_detector import RegimeDetector
from signals.kalman_agent import AdaptiveKalmanAgent
from governance.firewall import GovernanceEngine
from utils.logger import logger
def resolve_peak_nav(account_nav: float, redis_client=None, peak_file_path: str = "logs/peak_nav.json") -> float:
    """
    Resolves the peak NAV using Redis with a disk-backed fallback.
    """
    peak_nav = account_nav
    stored_peak_val = None
    
    if redis_client:
        try:
            stored_peak = redis_client.get("peak_nav")
            if stored_peak:
                stored_peak_val = float(stored_peak)
        except Exception as e:
            logger.info(f"Redis peak_nav fetch failed: {e}")
            
    if stored_peak_val is None and os.path.exists(peak_file_path):
        try:
            import json
            with open(peak_file_path, "r") as f:
                data = json.load(f)
                if isinstance(data, dict) and "peak_nav" in data:
                    stored_peak_val = float(data["peak_nav"])
                elif isinstance(data, (int, float)):
                    stored_peak_val = float(data)
        except Exception as e:
            logger.info(f"Disk peak_nav fallback read failed: {e}")
            
    if stored_peak_val is not None:
        peak_nav = max(stored_peak_val, account_nav)
        
    return peak_nav


class TradingSystem:
    def __init__(self):
        self.alpaca_client = AlpacaTradingClient()
        self.order_manager = OrderManager(self.alpaca_client)
        self.data_fetcher = AlpacaDataFetcher()
        
        self.aligner = TemporalAligner(frequency='B')
        self.pca = PCAOrthogonalizer(n_components=3)
        self.smoother = EMASmoother(alpha=0.30)
        self.isolator = AlphaIsolator(alpha=0.30)
        self.ranker = PortfolioRanker()
        
        # New Multi-Agent Ensemble
        self.regime_detector = RegimeDetector()
        self.kalman_agent = AdaptiveKalmanAgent()
        self.volatility_guard = VolatilityGuard(tp_multiplier=2.5, sl_multiplier=1.5)
        
        try:
            self.redis_client = redis.Redis(host=os.getenv('REDIS_HOST', 'localhost'), port=6379, db=0)
        except Exception as e:
            logger.exception(f"Redis initialization failed: {e}")
            discord_alerter.send_alert(f"🚨 **URGENT:** Redis initialization failed!\nError: `{e}`")
            self.redis_client = None
            
        self.ensemble = EnsembleAgent(agent_names=['chronos', 'kalman'], redis_client=self.redis_client)
        
        self.firewall = GovernanceEngine(var_limit=0.05, 
                                         global_max_leverage=2.0, 
                                         global_max_drawdown=0.10,
                                         kalman_max_concentration=0.20,
                                         chronos_max_concentration=0.20)
        
        self.context_window = 100
        self.inference_url = "http://localhost:8000/v1/timeseries/forecast"
        
    async def fetch_historical_data(self) -> pd.DataFrame:
        symbols = [
            "AAPL", "MSFT", "NVDA", "AMZN", "META", "GOOGL", "TSLA", "BRK.B", "UNH", "JNJ", "SPY",
            "JPM", "V", "PG", "HD", "CVX", "LLY", "MA", "ABBV", "PEP", "KO"
        ]
        return await self.data_fetcher.fetch_historical_data(symbols, days=150)
        
    async def _execute_position_change(self, asset, delta_qty, current_qty, label=""):
        import asyncio
        from alpaca.trading.requests import GetOrdersRequest
        from alpaca.trading.enums import QueryOrderStatus

        abs_delta = abs(delta_qty)
        action = 'BUY' if delta_qty > 0 else 'SELL'
        last_trade = None
        total_reduce_qty = 0
        target_qty = current_qty + delta_qty
        
        # Check if we are crossing zero (flipping position)
        if current_qty != 0 and (target_qty * current_qty < 0):
            # We are crossing zero. Split into REDUCE and ENTRY.
            reduce_action = 'SELL' if current_qty > 0 else 'BUY'
            reduce_qty = abs(current_qty)
            total_reduce_qty = reduce_qty
            
            if reduce_qty >= 1.0:
                logger.info(f"Routing {reduce_action} {reduce_qty:.4f} {asset} [{label} - REDUCE] via Alpaca as Market Order...")
                reduce_order = self.order_manager.create_market_order(asset, reduce_action, reduce_qty)
                if reduce_order:
                    trade = await self.order_manager.route_order_async(reduce_order)
                    # Poll for fill to avoid race condition
                    if trade and hasattr(trade, 'id'):
                        logger.info(f"Waiting for {asset} REDUCE order to fill before submitting ENTRY order...")
                        filled = False
                        for _ in range(60): # up to 120 seconds
                            try:
                                order_status = self.alpaca_client.client.get_order_by_id(trade.id)
                                if order_status.status.name == 'FILLED':
                                    filled = True
                                    break
                                elif order_status.status.name in ['CANCELED', 'REJECTED', 'EXPIRED']:
                                    logger.error(f"REDUCE order {trade.id} failed with status {order_status.status.name}")
                                    break
                            except Exception as e:
                                logger.error(f"Error checking order status: {e}")
                            await asyncio.sleep(2.0)
                        
                        if not filled:
                            logger.error(f"REDUCE order for {asset} did not fill. Skipping ENTRY order.")
                            return abs_delta, target_qty, trade, total_reduce_qty
                            
            # Now the remaining delta is the new entry
            entry_qty = abs(target_qty)
            entry_action = 'BUY' if target_qty > 0 else 'SELL'
            if entry_qty >= 1.0:
                logger.info(f"Routing {entry_action} {entry_qty:.4f} {asset} [{label} - ENTRY] via Alpaca as Market Order...")
                entry_order = self.order_manager.create_market_order(asset, entry_action, entry_qty)
                if entry_order:
                    last_trade = await self.order_manager.route_order_async(entry_order)
                    
            return abs_delta, target_qty, last_trade, total_reduce_qty
            
        else:
            # Not crossing zero, single order is fine
            if abs_delta >= 1.0:
                logger.info(f"Routing {action} {abs_delta:.4f} {asset} [{label}] via Alpaca as Market Order...")
                order = self.order_manager.create_market_order(asset, action, abs_delta)
                if order:
                    last_trade = await self.order_manager.route_order_async(order)
                    
            return abs_delta, target_qty, last_trade, 0

    async def execute_daily_loop(self):
        logger.info("Starting daily execution loop...")
        
        # Pre-execution: Clean slate to prevent overlapping bounds
        await self.alpaca_client.async_cancel_all_and_wait()
        
        clock = self.alpaca_client.get_clock()
        if clock and not clock.is_open:
            logger.info("Market is currently closed. Daily execution aborted.")
            return

        raw_data = await self.fetch_historical_data()
        macro_data = await self.data_fetcher.fetch_macro_data(days=150)

        
        full_idx = pd.bdate_range(start=raw_data.index.min(), end=raw_data.index.max())
        market_data = raw_data.reindex(full_idx)
        
        if len(market_data) < self.context_window:
            logger.info(f"WARMUP STATE ENFORCEMENT: Accumulated {len(market_data)}/{self.context_window} days. Execution strictly blocked.")
            return
            
        logger.info("Warmup complete. 100-day context window verified.")
        
        # 1. Regime Detection
        regime = self.regime_detector.detect(market_data, benchmark_symbol='SPY')
        logger.info(f"Current Market Regime: {regime}")
        
        # 2. Temporal Alignment
        aligned_data = market_data
        close_data = aligned_data.xs('close', level=1, axis=1)
        returns_data = close_data.pct_change().dropna()
        
        # 3. Agent 1: Chronos-2
        residuals = self.pca.orthogonalize(returns_data)
        smoothed_residuals = self.smoother.smooth(residuals)
        
        predictions_list = []
        for asset in smoothed_residuals.columns:
            asset_payload = []
            for date, val in smoothed_residuals[asset].items():
                naive_date = date.tz_localize(None) if date.tzinfo else date
                if pd.notna(val) and naive_date in macro_data.index:
                    spy_ret = returns_data.loc[date, 'SPY'] if 'SPY' in returns_data.columns and pd.notna(returns_data.loc[date, 'SPY']) else 0.0
                    vix = macro_data.loc[naive_date, 'vix_close'] if pd.notna(macro_data.loc[naive_date, 'vix_close']) else 20.0
                    tnx = macro_data.loc[naive_date, 'tnx_yield'] if pd.notna(macro_data.loc[naive_date, 'tnx_yield']) else 4.0
                    
                    asset_payload.append({
                        "item_id": asset, 
                        "timestamp": str(naive_date), 
                        "target": val,
                        "vix_close": vix,
                        "tnx_yield": tnx,
                        "sector_etf": spy_ret
                    })
            if asset_payload:
                try:
                    response = requests.post(self.inference_url, json={"data": asset_payload})
                    response.raise_for_status()
                    predictions_list.extend(response.json()["predictions"])
                except Exception as e:
                    logger.exception(f"Failed inference for {asset}: {e}")
                    discord_alerter.send_alert(f"🚨 **WARNING:** Failed inference for {asset}!\\nError: `{e}`")
                    
        if predictions_list:
            predictions = pd.DataFrame(predictions_list).set_index("item_id")
            expected_forward = predictions['0.5'] 
            latest_smoothed = smoothed_residuals.iloc[-1]
            alpha_signal = self.isolator.isolate(expected_forward, latest_smoothed)
            
            alpha_df = pd.DataFrame([alpha_signal])
            chronos_weights = self.ranker.rank_and_normalize(alpha_df).iloc[0]
        else:
            logger.info("All inference requests failed. Defaulting Chronos weights to 0.")
            chronos_weights = pd.Series(0, index=close_data.columns)
            predictions = None
            
        # 4. Agent 2: Adaptive Kalman Momentum
        kalman_weights = self.kalman_agent.generate_signal(market_data)
        
        raw_agent_weights = {
            'chronos': chronos_weights,
            'kalman': kalman_weights
        }
        
        # 5. Thompson Sampling Blending
        trust_weights = self.ensemble.sample_trust_weights(regime)
        logger.info(f"Thompson Sampling Trust Weights: {trust_weights}")
        
        # Ensure indexes match before passing to firewall
        for agent_name, weight_series in raw_agent_weights.items():
            raw_agent_weights[agent_name] = weight_series.reindex(close_data.columns).fillna(0)
            
        # 6. Deterministic Risk Governance Firewall (Agent-Aware)
        account_nav = self.alpaca_client.get_account_value()
        if account_nav == 0:
            account_nav = 100000.0 # Paper Trading fallback
            
        # Durable Peak NAV with Redis + local disk fallback
        peak_file = "logs/peak_nav.json"
        peak_nav = resolve_peak_nav(account_nav, self.redis_client, peak_file)
            
        if self.redis_client:
            try:
                self.redis_client.set("peak_nav", peak_nav)
            except Exception as e:
                logger.info(f"Redis peak_nav update failed: {e}")
                
        try:
            import json
            os.makedirs("logs", exist_ok=True)
            with open(peak_file, "w") as f:
                json.dump({"peak_nav": peak_nav}, f)
        except Exception as e:
            logger.info(f"Disk peak_nav save failed: {e}")
                
        approved_weights, constrained_agent_weights = self.firewall.evaluate_trades(raw_agent_weights, trust_weights, predictions, account_nav, peak_nav=peak_nav)
        
        # 7. Asynchronous Route Delta Orders
        logger.info("Formulating agent-aware delta orders mapped to Governance bounds...")
        
        open_positions = self.alpaca_client.get_open_positions()
        current_holdings = {
            pos.symbol: (float(pos.qty) if pos.side.name == 'LONG' else -abs(float(pos.qty))) 
            for pos in open_positions
        }
        
        usable_nav = account_nav * 0.95 # 5% safety buffer
        all_assets = set(approved_weights.index).union(current_holdings.keys())
        
        submitted_order_ids = []
        
        for asset in all_assets:
            latest_price = close_data.iloc[-1].get(asset, None) if asset in close_data.columns else None
            
            if pd.isna(latest_price) or latest_price <= 0:
                if approved_weights.get(asset, 0.0) != 0 or current_holdings.get(asset, 0.0) != 0:
                    logger.info(f"Skipping {asset} due to missing price data.")
                continue
                
            initial_qty = current_holdings.get(asset, 0.0)
            current_qty = initial_qty
            
            target_weight = approved_weights.get(asset, 0.0)
            target_qty = (target_weight * usable_nav) / latest_price
            delta_qty = target_qty - current_qty
            
            if abs(delta_qty) >= 1.0:
                _, current_qty, trade, _ = await self._execute_position_change(
                    asset, delta_qty, current_qty, label="Rebalance/GTC"
                )
                if trade and hasattr(trade, 'id'):
                    submitted_order_ids.append(str(trade.id))
                
        # --- WAIT FOR ORDERS TO FILL ---
        if submitted_order_ids:
            logger.info(f"Waiting for {len(submitted_order_ids)} market orders to fill (up to 30 seconds)...")
            from alpaca.trading.requests import GetOrdersRequest
            from alpaca.trading.enums import QueryOrderStatus
            import asyncio
            
            for _ in range(30):
                req = GetOrdersRequest(status=QueryOrderStatus.OPEN)
                open_orders = self.alpaca_client.client.get_orders(filter=req)
                
                pending = [o for o in open_orders if str(o.id) in submitted_order_ids]
                if not pending:
                    logger.info("All market orders have filled.")
                    break
                    
                logger.info(f"Still waiting on {len(pending)} orders to fill...")
                await asyncio.sleep(1.0)
            else:
                logger.info("Timeout reached. Canceling remaining unfilled portions of market orders...")
                for order_id in submitted_order_ids:
                    try:
                        self.alpaca_client.client.cancel_order_by_id(order_id)
                    except Exception as e:
                        logger.warning(f"Failed to cancel un-filled portion of order {order_id}: {e}")
                # Give backend a moment to process the targeted cancellations
                await asyncio.sleep(2.0)
                
        # --- UNIVERSAL OCO BRACKETING (THE GUARD) ---
        logger.info("Canceling old bracket orders to free up shares...")
        await self.alpaca_client.async_cancel_all_and_wait()
        
        final_positions = self.alpaca_client.get_open_positions()
        logger.info(f"Applying protective OCO brackets to {len(final_positions)} open positions...")
        
        # Fetch live prices for bracket calculation
        symbols_to_protect = [pos.symbol for pos in final_positions]
        live_prices = await self.data_fetcher.fetch_live_prices(symbols_to_protect) if symbols_to_protect else {}        
        for pos in final_positions:
            asset = pos.symbol
            qty = abs(float(pos.qty))
            
            if qty < 1.0:
                continue
                
            latest_price = live_prices.get(asset, None)
            if latest_price is None or latest_price <= 0:
                # Fallback to historical if live fails
                latest_price = close_data.iloc[-1].get(asset, None) if asset in close_data.columns else None
                
            if pd.isna(latest_price) or latest_price <= 0:
                logger.info(f"Skipping bracket for {asset} due to missing price data.")
                continue
                
            held_action = 'BUY' if float(pos.qty) > 0 else 'SELL'
            held_tp, held_sl = None, None
            if asset in returns_data.columns:
                held_tp, held_sl = self.volatility_guard.get_bracket_bounds(held_action, latest_price, returns_data[asset])
            
            if held_tp is not None and held_sl is not None:
                oco_side = 'SELL' if float(pos.qty) > 0 else 'BUY'
                from alpaca.trading.enums import TimeInForce
                logger.info(f"Routing {oco_side} {qty:.4f} {asset} [PROTECT HELD] via Alpaca as OCO Order...")
                order = self.order_manager.create_oco_order(asset, oco_side, qty, held_tp, held_sl, time_in_force=TimeInForce.GTC)
                if order:
                    await self.order_manager.route_order_async(order)
                       # --- UNPROTECTED POSITION VERIFICATION ---
        try:
            from alpaca.trading.requests import GetOrdersRequest
            from alpaca.trading.enums import QueryOrderStatus
            
            check_positions = self.alpaca_client.get_open_positions()
            req = GetOrdersRequest(status=QueryOrderStatus.OPEN)
            open_orders = self.alpaca_client.client.get_orders(filter=req)
            open_order_symbols = {order.symbol for order in open_orders} if open_orders else set()
            
            unprotected_symbols = [
                pos.symbol for pos in check_positions 
                if abs(float(pos.qty)) >= 1.0 and pos.symbol not in open_order_symbols
            ]
            
            if unprotected_symbols:
                alert_msg = f"🚨 **UNPROTECTED POSITION WARNING:** The following open positions have no corresponding active OCO orders: {', '.join(unprotected_symbols)}"
                logger.error(alert_msg)
                discord_alerter.send_alert(alert_msg)
            else:
                logger.info("Protection verification passed: All open positions have corresponding open orders.")
        except Exception as e:
            logger.exception(f"Failed during unprotected position verification check: {e}")
            discord_alerter.send_alert(f"🚨 **WARNING:** Failed during unprotected position verification check!\nError: `{e}`")

        logger.info("Loop execution complete.")
        
        summary_lines = ["📈 **Daily Execution Summary**"]
        if final_positions:
            for pos in final_positions:
                summary_lines.append(f"- {pos.symbol}: {pos.qty} shares @ ${pos.avg_entry_price}")
        else:
            summary_lines.append("No open positions.")
            
        discord_alerter.send_alert("\n".join(summary_lines))

if __name__ == "__main__":
    system = TradingSystem()
    asyncio.run(system.execute_daily_loop())
