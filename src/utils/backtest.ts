import type { BacktestPoint, FundHistory, HistoryPoint } from "./models";

const TAX_RATE = 37.84 / 100;

/** Convert Nordnet cumulative return % into a relative price index. */
export function toPriceIndex(points: HistoryPoint[]): { t: number; price: number }[] {
	return points.map((p) => ({
		t: p.t,
		price: 100 * (1 + p.v / 100),
	}));
}

export function earliestHistoryDate(histories: FundHistory[]): Date | null {
	let min: number | null = null;
	for (const h of histories) {
		const t = h.points[0]?.t;
		if (t == null) continue;
		min = min == null ? t : Math.min(min, t);
	}
	return min == null ? null : new Date(min);
}

function startOfMonth(d: Date): Date {
	return new Date(d.getFullYear(), d.getMonth(), 1);
}

function addMonths(d: Date, n: number): Date {
	return new Date(d.getFullYear(), d.getMonth() + n, 1);
}

/** Last known price on or before timestamp. */
function priceOnOrBefore(
	series: { t: number; price: number }[],
	ts: number,
): number | null {
	let lo = 0;
	let hi = series.length - 1;
	let ans: number | null = null;
	while (lo <= hi) {
		const mid = (lo + hi) >> 1;
		if (series[mid].t <= ts) {
			ans = series[mid].price;
			lo = mid + 1;
		} else {
			hi = mid - 1;
		}
	}
	return ans;
}

export function monthEndsBetween(start: Date, end: Date): Date[] {
	const months: Date[] = [];
	let cursor = startOfMonth(start);
	const last = startOfMonth(end);
	while (cursor <= last) {
		// use last day-ish of month for pricing: month start + 1 month - 1 day
		const sample = new Date(cursor.getFullYear(), cursor.getMonth() + 1, 0);
		months.push(sample);
		cursor = addMonths(cursor, 1);
	}
	return months;
}

/**
 * DCA backtest using Nordnet cumulative-return series as a price index.
 * Fees are applied monthly as fund_calculated_fee / 12.
 */
export function backtestFund(
	history: FundHistory,
	startDate: Date,
	endDate: Date,
	startAmount: number,
	monthlyContribution: number,
	yearlyFeePct: number,
): BacktestPoint[] {
	const series = toPriceIndex(history.points);
	if (series.length === 0) return [];

	const months = monthEndsBetween(startDate, endDate);
	if (months.length === 0) return [];

	const monthlyFee = yearlyFeePct / (100 * 12);
	const points: BacktestPoint[] = [];

	let units = 0;
	let contributed = 0;

	for (let i = 0; i < months.length; i++) {
		const date = months[i];
		const price = priceOnOrBefore(series, date.getTime());
		if (price == null || price <= 0) continue;

		const contribution = i === 0 ? startAmount : monthlyContribution;
		units += contribution / price;
		contributed += contribution;

		const feeUnits = units * monthlyFee;
		const feeNok = feeUnits * price;
		units -= feeUnits;

		const value = units * price;
		const profit = value - contributed;
		const tax = Math.max(0, profit) * TAX_RATE;
		const afterTax = contributed + (profit - tax);

		points.push({
			date,
			value,
			contributed,
			fee: feeNok,
			tax,
			afterTax,
		});
	}

	return points;
}

/** Bank path over the same calendar months using a flat nominal rate. */
export function backtestBank(
	months: Date[],
	startAmount: number,
	monthlyContribution: number,
	yearlyRatePct: number,
): BacktestPoint[] {
	const monthlyRate = yearlyRatePct / (100 * 12);
	const points: BacktestPoint[] = [];
	let value = 0;
	let contributed = 0;

	for (let i = 0; i < months.length; i++) {
		const contribution = i === 0 ? startAmount : monthlyContribution;
		if (i === 0) {
			value = contribution;
		} else {
			value = value * (1 + monthlyRate) + contribution;
		}
		contributed += contribution;
		points.push({
			date: months[i],
			value,
			contributed,
			fee: 0,
			tax: 0,
			afterTax: value,
		});
	}
	return points;
}

export function toInputDate(d: Date): string {
	const y = d.getFullYear();
	const m = String(d.getMonth() + 1).padStart(2, "0");
	const day = String(d.getDate()).padStart(2, "0");
	return `${y}-${m}-${day}`;
}
