//+------------------------------------------------------------------+
//|                                      GoldTrader_MTF_EA.mq5       |
//|                        黄金交易EA - 多时间框架RSI+EMA策略         |
//|                        目标: $1560 -> $3000                      |
//+------------------------------------------------------------------+
#property copyright "GoldTrader v1.0"
#property version   "1.00"
#property description "Multi-Timeframe RSI + EMA Strategy for XAUUSD"
#property strict

#include <Trade\Trade.mqh>

//==================== 输入参数 ====================
input group "=== 账户设置 ==="
input double Inp_TargetBalance    = 3000.0;
input double Inp_InitialBalance   = 1560.0;
input ulong  Inp_MagicNumber      = 20260909;
input string Inp_Symbol           = "XAUUSDc";

input group "=== 仓位管理 ==="
input double Inp_LotBase          = 0.05;
input double Inp_LotMax           = 0.20;
input int    Inp_MaxPositions     = 3;

input group "=== 止盈止损 ==="
input double Inp_TP_Amount        = 50.0;
input double Inp_SL_Amount        = 30.0;

input group "=== 风控 ==="
input int    Inp_CooldownMinutes  = 3;
input int    Inp_MaxLossDaily     = 50;
input int    Inp_ConsecLossPause  = 2;

input group "=== RSI参数 ==="
input int    Inp_RSI_Period       = 14;
input int    Inp_RSI_H1_Buy       = 30;
input int    Inp_RSI_H1_Sell      = 70;
input int    Inp_RSI_M15_Buy      = 35;
input int    Inp_RSI_M15_Sell     = 65;

input group "=== EMA参数 ==="
input int    Inp_EMA_Fast         = 5;
input int    Inp_EMA_Mid          = 20;
input int    Inp_EMA_Slow         = 50;

//==================== 全局变量 ====================
CTrade         trade;
datetime       lastTradeTime      = 0;
int            consecLosses       = 0;
double         dailyPnL           = 0.0;
string         lastTradeDate      = "";
int            tradeCount         = 0;
double         startBalance       = 0.0;

//==================== 辅助函数 ====================
double CalcRSI(ENUM_TIMEFRAMES tf, int period)
  {
   double prices[];
   ArraySetAsSeries(prices, true);
   if(CopyClose(Inp_Symbol, tf, 0, period + 1, prices) < period + 1) return 50.0;
   double gains = 0, losses = 0;
   for(int i = 1; i <= period; i++)
     {
      double d = prices[i-1] - prices[i];
      if(d > 0) gains += d;
      else losses -= d;
     }
   double avgGain = gains / period;
   double avgLoss = losses / period;
   if(avgLoss == 0) return 100.0;
   return 100.0 - (100.0 / (1.0 + avgGain / avgLoss));
  }

double CalcEMA(double &data[], int period)
  {
   if(ArraySize(data) < period) return 0.0;
   double k = 2.0 / (period + 1);
   double ema = data[0];
   for(int i = 1; i < period; i++) ema = data[i] * k + ema * (1 - k);
   return ema;
  }

void Log(string msg, string level="INFO")
  {
   string ts = TimeToString(TimeCurrent(), TIME_SECONDS);
   Print("[", ts, "] [", level, "] ", msg);
  }

double GetBalance()
  {
   double bal = AccountInfoDouble(ACCOUNT_BALANCE);
   return (bal > 0.0) ? bal : 0.0;
  }

double CalcPositionPnL(ulong ticket)
  {
   if(!PositionSelectByTicket(ticket)) return 0.0;
   double openPrice = PositionGetDouble(POSITION_PRICE_OPEN);
   double volume    = PositionGetDouble(POSITION_VOLUME);
   long   type      = PositionGetInteger(POSITION_TYPE);
   double bid       = SymbolInfoDouble(Inp_Symbol, SYMBOL_BID);
   double pnl = 0.0;
   if(type == POSITION_TYPE_BUY)
      pnl = (bid - openPrice) * volume * 100.0;
   else
      pnl = (openPrice - bid) * volume * 100.0;
   return pnl;
  }

double CalcTotalPnL()
  {
   double total = 0.0;
   for(int i = PositionsTotal() - 1; i >= 0; i--)
     {
      ulong ticket = PositionGetTicket(i);
      if(ticket > 0 && PositionGetInteger(POSITION_MAGIC) == Inp_MagicNumber)
        total += CalcPositionPnL(ticket);
     }
   return total;
  }

int GetPositionCount()
  {
   int count = 0;
   for(int i = PositionsTotal() - 1; i >= 0; i--)
     {
      ulong ticket = PositionGetTicket(i);
      if(ticket > 0 && PositionGetInteger(POSITION_MAGIC) == Inp_MagicNumber)
        count++;
     }
   return count;
  }

int AnalyzeSignal()
  {
   int score = 0;
   double rsiH1 = CalcRSI(PERIOD_H1, Inp_RSI_Period);
   double rsiM15 = CalcRSI(PERIOD_M15, Inp_RSI_Period);
   
   if(rsiH1 < Inp_RSI_H1_Buy) score += 4;
   else if(rsiH1 < 40) score += 2;
   else if(rsiH1 > Inp_RSI_H1_Sell) score -= 4;
   else if(rsiH1 > 60) score -= 2;
   
   if(rsiM15 < Inp_RSI_M15_Buy) score += 2;
   else if(rsiM15 > Inp_RSI_M15_Sell) score -= 2;
   
   double h1Closes[];
   ArraySetAsSeries(h1Closes, true);
   CopyClose(Inp_Symbol, PERIOD_H1, 0, 50, h1Closes);
   
   double ema5  = CalcEMA(h1Closes, Inp_EMA_Fast);
   double ema20 = CalcEMA(h1Closes, Inp_EMA_Mid);
   double ema50 = CalcEMA(h1Closes, Inp_EMA_Slow);
   double price = SymbolInfoDouble(Inp_Symbol, SYMBOL_BID);
   
   if(ema5 > ema20 && ema20 > ema50) score += 3;
   else if(ema5 < ema20 && ema20 < ema50) score -= 3;
   else if(ema5 > ema20) score += 1;
   else if(ema5 < ema20) score -= 1;
   
   if(price < ema20 * 0.995) score += 1;
   else if(price > ema20 * 1.005) score -= 1;
   
   double m5Closes[];
   ArraySetAsSeries(m5Closes, true);
   CopyClose(Inp_Symbol, PERIOD_M5, 0, 30, m5Closes);
   if(ArraySize(m5Closes) >= 5)
     {
      double m5ma = 0;
      for(int i = 0; i < 5; i++) m5ma += m5Closes[i];
      m5ma /= 5;
      if(rsiH1 < 40 && m5ma > m5Closes[0]) score += 1;
      else if(rsiH1 > 60 && m5ma < m5Closes[0]) score -= 1;
     }
   return score;
  }

double CalcLot(int score, double balance)
  {
   double lot = Inp_LotBase * (1.0 + MathAbs(score) * 0.1);
   lot = MathMin(Inp_LotMax, lot);
   double factor = MathMin(2.0, balance / 2000.0);
   lot *= factor;
   double step = SymbolInfoDouble(Inp_Symbol, SYMBOL_VOLUME_STEP);
   lot = MathRound(lot / step) * step;
   double minLot = SymbolInfoDouble(Inp_Symbol, SYMBOL_VOLUME_MIN);
   if(lot < minLot) lot = minLot;
   return lot;
  }

bool OpenPosition(ENUM_ORDER_TYPE type, double lot)
  {
   MqlTradeRequest request = {};
   MqlTradeResult  result  = {};
   
   double price = (type == ORDER_TYPE_BUY) ? 
                  SymbolInfoDouble(Inp_Symbol, SYMBOL_ASK) : 
                  SymbolInfoDouble(Inp_Symbol, SYMBOL_BID);
   
   double slPct = Inp_SL_Amount / (lot * 100.0 * price) * 100.0;
   double tpPct = Inp_TP_Amount / (lot * 100.0 * price) * 100.0;
   
   double sl = (type == ORDER_TYPE_BUY) ? price * (1.0 - slPct / 100.0) : price * (1.0 + slPct / 100.0);
   double tp = (type == ORDER_TYPE_BUY) ? price * (1.0 + tpPct / 100.0) : price * (1.0 - tpPct / 100.0);
   
   request.action      = TRADE_ACTION_DEAL;
   request.symbol      = Inp_Symbol;
   request.volume      = lot;
   request.type        = type;
   request.price       = price;
   request.sl          = NormalizeDouble(sl, (int)SymbolInfoInteger(Inp_Symbol, SYMBOL_DIGITS));
   request.tp          = NormalizeDouble(tp, (int)SymbolInfoInteger(Inp_Symbol, SYMBOL_DIGITS));
   request.deviation   = 30;
   request.magic       = Inp_MagicNumber;
   request.comment     = "GoldTrader_MTF";
   request.type_filling= ORDER_FILLING_FOK;
   
   if(!OrderSend(request, result))
     {
      Log("OrderSend failed: rc=" + IntegerToString(result.retcode), "ERROR");
      return false;
     }
   if(result.retcode != TRADE_RETCODE_DONE)
     {
      Log("Trade error: rc=" + IntegerToString(result.retcode) + " " + result.comment, "ERROR");
      return false;
     }
   Log("Opened " + EnumToString(type) + " " + DoubleToString(lot, 2) + "@" + DoubleToString(price, 2) + " ticket=" + IntegerToString(result.order), "TRADE");
   return true;
  }

bool ClosePosition(ulong ticket)
  {
   if(!PositionSelectByTicket(ticket)) return false;
   MqlTradeRequest request = {};
   MqlTradeResult  result  = {};
   long type = PositionGetInteger(POSITION_TYPE);
   double price = (type == POSITION_TYPE_BUY) ? 
                  SymbolInfoDouble(Inp_Symbol, SYMBOL_BID) : 
                  SymbolInfoDouble(Inp_Symbol, SYMBOL_ASK);
   request.action      = TRADE_ACTION_DEAL;
   request.symbol      = Inp_Symbol;
   request.volume      = PositionGetDouble(POSITION_VOLUME);
   request.type        = (type == POSITION_TYPE_BUY) ? ORDER_TYPE_SELL : ORDER_TYPE_BUY;
   request.position    = ticket;
   request.price       = price;
   request.deviation   = 30;
   request.magic       = Inp_MagicNumber;
   request.type_filling= ORDER_FILLING_FOK;
   if(!OrderSend(request, result)) return false;
   return (result.retcode == TRADE_RETCODE_DONE);
  }

//==================== EA主函数 ====================
int OnInit()
  {
   trade.SetExpertMagicNumber(Inp_MagicNumber);
   trade.SetDeviationInPoints(30);
   trade.SetTypeFilling(ORDER_FILLING_FOK);
   trade.SetAsyncMode(false);
   startBalance = GetBalance();
   if(startBalance == 0.0) startBalance = Inp_InitialBalance;
   Log("========================================");
   Log("GoldTrader MTF EA v1.0 STARTED");
   Log("Target: $" + DoubleToString(Inp_TargetBalance, 0) + " | Initial: $" + DoubleToString(Inp_InitialBalance, 0));
   Log("Symbol: " + Inp_Symbol + " | Magic: " + IntegerToString(Inp_MagicNumber));
   Log("Lot: " + DoubleToString(Inp_LotBase, 2) + "~" + DoubleToString(Inp_LotMax, 2));
   Log("TP: $" + DoubleToString(Inp_TP_Amount, 0) + " | SL: $" + DoubleToString(Inp_SL_Amount, 0));
   Log("Cooldown: " + IntegerToString(Inp_CooldownMinutes) + "min | MaxPos: " + IntegerToString(Inp_MaxPositions));
   Log("========================================");
   MqlDateTime dt;
   TimeToStruct(TimeCurrent(), dt);
   lastTradeDate = StringFormat("%04d.%02d.%02d", dt.year, dt.mon + 1, dt.day);
   return(INIT_SUCCEEDED);
  }

void OnDeinit(const int reason)
  {
   double bal = GetBalance();
   Log("EA Stopped | Final: $" + DoubleToString(bal, 2) + " | Trades: " + IntegerToString(tradeCount), "INFO");
  }

void OnTick()
  {
   double balance = GetBalance();
   if(balance == 0.0) return;
   
   MqlDateTime dt;
   TimeToStruct(TimeCurrent(), dt);
   string today = StringFormat("%04d.%02d.%02d", dt.year, dt.mon + 1, dt.day);
   if(today != lastTradeDate)
     { dailyPnL = 0.0; lastTradeDate = today; }
   
   if(balance >= Inp_TargetBalance)
     {
      Log("*** TARGET REACHED! $" + DoubleToString(balance, 2) + " ***", "SUCCESS");
      for(int i = PositionsTotal() - 1; i >= 0; i--)
        { ulong t = PositionGetTicket(i); if(t > 0 && PositionGetInteger(POSITION_MAGIC) == Inp_MagicNumber) ClosePosition(t); }
      return;
     }
   if(balance <= Inp_InitialBalance * 0.85)
     {
      Log("*** CAPITAL PROTECTION! $" + DoubleToString(balance, 2) + " ***", "WARNING");
      for(int i = PositionsTotal() - 1; i >= 0; i--)
        { ulong t = PositionGetTicket(i); if(t > 0 && PositionGetInteger(POSITION_MAGIC) == Inp_MagicNumber) ClosePosition(t); }
      return;
     }
   
   static datetime lastLog = 0;
   if(TimeCurrent() - lastLog > 30)
     {
      double pnl = CalcTotalPnL();
      double progress = (balance - Inp_InitialBalance) / (Inp_TargetBalance - Inp_InitialBalance) * 100.0;
      Log("Bal=$" + DoubleToString(balance, 2) + " PnL=$" + DoubleToString(pnl, 2) + " Prog=" + DoubleToString(progress, 1) + "% Pos=" + IntegerToString(GetPositionCount()));
      lastLog = TimeCurrent();
     }
   
   for(int i = PositionsTotal() - 1; i >= 0; i--)
     {
      ulong ticket = PositionGetTicket(i);
      if(ticket == 0 || PositionGetInteger(POSITION_MAGIC) != Inp_MagicNumber) continue;
      double pnl = CalcPositionPnL(ticket);
      if(pnl >= Inp_TP_Amount)
        {
         if(ClosePosition(ticket))
           { consecLosses = 0; dailyPnL += pnl; tradeCount++; Log("TP +$" + DoubleToString(pnl, 2) + " closed #" + IntegerToString(ticket), "SUCCESS"); return; }
        }
      if(pnl <= -Inp_SL_Amount)
        {
         if(ClosePosition(ticket))
           { consecLosses++; dailyPnL += pnl; tradeCount++; Log("SL -$" + DoubleToString(MathAbs(pnl), 2) + " closed #" + IntegerToString(ticket), "WARNING"); return; }
        }
     }
   
   if(consecLosses >= Inp_ConsecLossPause) return;
   if(dailyPnL <= -Inp_MaxLossDaily) return;
   if(GetPositionCount() >= Inp_MaxPositions) return;
   if(TimeCurrent() - lastTradeTime < Inp_CooldownMinutes * 60) return;
   
   int score = AnalyzeSignal();
   double rsiH1 = CalcRSI(PERIOD_H1, Inp_RSI_Period);
   double rsiM15 = CalcRSI(PERIOD_M15, Inp_RSI_Period);
   Log("Analysis: RSI_H1=" + DoubleToString(rsiH1, 1) + " RSI_M15=" + DoubleToString(rsiM15, 1) + " Score=" + IntegerToString(score), "INFO");
   
   double lot = CalcLot(score, balance);
   if(score >= 4)
     {
      if(OpenPosition(ORDER_TYPE_BUY, lot)) { lastTradeTime = TimeCurrent(); consecLosses = 0; }
     }
   else if(score <= -4)
     {
      if(OpenPosition(ORDER_TYPE_SELL, lot)) { lastTradeTime = TimeCurrent(); consecLosses = 0; }
     }
  }
//+------------------------------------------------------------------+
