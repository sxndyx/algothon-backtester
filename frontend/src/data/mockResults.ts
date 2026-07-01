export type DailyRecord = {
  day: number;
  gross_pnl: number;
  net_pnl: number;
  cumulative_pnl: number;
  turnover: number;
  commission: number;
  num_traded_instruments: number;
  num_clipped_instruments: number;
};

export type BacktestResults = {
  metadata: {
    n_instruments: number;
    n_days: number;
    commission_rate: number;
    position_limit_dollars: number;
    deterministic: boolean;
    uses_simulated_price_data: boolean;
  };
  summary: {
    score: number;
    total_pnl: number;
    mean_daily_pnl: number;
    std_daily_pnl: number;
    max_drawdown: number;
    total_commission: number;
    total_turnover: number;
    total_trades: number;
    clipping_event_count: number;
  };
  daily_records: DailyRecord[];
  series: {
    daily_pnl: number[];
    cumulative_pnl: number[];
    drawdown: number[];
    daily_turnover: number[];
    daily_commission: number[];
  };
  positions: number[][];
  trades: number[][];
  clipping_events: Array<{
    day: number;
    num_clipped_instruments: number;
  }>;
};

const nInstruments = 50;
const nDays = 180;
const tradingDays = nDays - 1;

function rounded(value: number, digits = 2): number {
  return Number(value.toFixed(digits));
}

function makeMockResults(): BacktestResults {
  const dailyPnl: number[] = [];
  const cumulativePnl: number[] = [];
  const drawdown: number[] = [];
  const dailyTurnover: number[] = [];
  const dailyCommission: number[] = [];
  const positions: number[][] = [];
  const trades: number[][] = [];
  const dailyRecords: DailyRecord[] = [];
  const clippingEvents: BacktestResults["clipping_events"] = [];

  let runningPnl = 0;
  let peakPnl = 0;
  let totalTrades = 0;

  for (let day = 1; day <= tradingDays; day += 1) {
    const drift = day < 95 ? 22 : -4;
    const cycle = Math.sin(day / 8) * 210 + Math.cos(day / 17) * 115;
    const shock = day % 37 === 0 ? -780 : day % 53 === 0 ? 620 : 0;
    const netPnl = rounded(drift + cycle + shock);
    const turnover = rounded(14500 + Math.abs(Math.sin(day / 6)) * 52000 + day * 140);
    const commission = rounded(turnover * 0.001);
    const dayPositions: number[] = [];
    const dayTrades: number[] = [];
    let tradedInstruments = 0;

    runningPnl = rounded(runningPnl + netPnl);
    peakPnl = Math.max(peakPnl, runningPnl);

    for (let instrument = 0; instrument < nInstruments; instrument += 1) {
      const wave = Math.sin(day / 10 + instrument * 0.35);
      const desired = Math.round(wave * 45);
      const previous = positions[day - 2]?.[instrument] ?? 0;
      const trade = desired - previous;
      dayPositions.push(desired);
      dayTrades.push(trade);

      if (trade !== 0) {
        tradedInstruments += 1;
      }
    }

    totalTrades += tradedInstruments;

    if (day === 72 || day === 131) {
      clippingEvents.push({
        day,
        num_clipped_instruments: day === 72 ? 2 : 1,
      });
    }

    dailyPnl.push(netPnl);
    cumulativePnl.push(runningPnl);
    drawdown.push(rounded(runningPnl - peakPnl));
    dailyTurnover.push(turnover);
    dailyCommission.push(commission);
    positions.push(dayPositions);
    trades.push(dayTrades);
    dailyRecords.push({
      day,
      gross_pnl: rounded(netPnl + commission),
      net_pnl: netPnl,
      cumulative_pnl: runningPnl,
      turnover,
      commission,
      num_traded_instruments: tradedInstruments,
      num_clipped_instruments:
        clippingEvents.find((event) => event.day === day)?.num_clipped_instruments ?? 0,
    });
  }

  const meanDailyPnl =
    dailyPnl.reduce((total, value) => total + value, 0) / dailyPnl.length;
  const variance =
    dailyPnl.reduce((total, value) => total + (value - meanDailyPnl) ** 2, 0) /
    dailyPnl.length;
  const stdDailyPnl = Math.sqrt(variance);

  return {
    metadata: {
      n_instruments: nInstruments,
      n_days: nDays,
      commission_rate: 0.001,
      position_limit_dollars: 10000,
      deterministic: true,
      uses_simulated_price_data: false,
    },
    summary: {
      score: rounded(meanDailyPnl - 0.1 * stdDailyPnl),
      total_pnl: rounded(runningPnl),
      mean_daily_pnl: rounded(meanDailyPnl),
      std_daily_pnl: rounded(stdDailyPnl),
      max_drawdown: rounded(Math.min(...drawdown)),
      total_commission: rounded(dailyCommission.reduce((total, value) => total + value, 0)),
      total_turnover: rounded(dailyTurnover.reduce((total, value) => total + value, 0)),
      total_trades: totalTrades,
      clipping_event_count: clippingEvents.length,
    },
    daily_records: dailyRecords,
    series: {
      daily_pnl: dailyPnl,
      cumulative_pnl: cumulativePnl,
      drawdown,
      daily_turnover: dailyTurnover,
      daily_commission: dailyCommission,
    },
    positions,
    trades,
    clipping_events: clippingEvents,
  };
}

export const mockResults = makeMockResults();
