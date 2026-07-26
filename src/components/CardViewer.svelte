<script lang="ts">
	import type { FundResult, Bank } from "../utils/models";
	import HelpIcon from "virtual:icons/material-symbols/help-outline";
	import IconoirFileNotFound from "virtual:icons/iconoir/file-not-found";

	export let fund: FundResult | null = null;
	export let bank: Bank | null = null;

	$: cardData = fund
		? {
				name: fund.instrument_info.name,
				iconUrl: fund.instrument_info.instrument_icon_url,
				rate: fund.historical_returns_info.yield_5y
					? (Number(fund.historical_returns_info.yield_5y.toFixed(2)) / 5).toFixed(2)
					: fund.historical_returns_info.yield_1y
						? Number(fund.historical_returns_info.yield_1y.toFixed(2)).toFixed(2)
						: "N/A",
				fee: fund.fund_info.fund_calculated_fee?.toFixed(2) ?? "N/A",
				url: `https://www.nordnet.no/market/funds?sortField=yield_1y&sortOrder=descending&freeTextSearch=${encodeURIComponent(fund.instrument_info.name)}`,
				kind: "Fund",
			}
		: bank
			? {
					name: bank.leverandorVisningsnavn + ` (${bank.navn})`,
					iconUrl: bank.icon_url || (bank.leverandorUrl.endsWith("/")
						? bank.leverandorUrl + "favicon.ico"
						: bank.leverandorUrl + "/favicon.ico"),
					rate: Number(bank.rentesats1)?.toFixed(2) ?? "N/A",
					fee: "N/A",
					url: bank.leverandorUrl,
					kind: "Bank",
				}
			: null;
</script>

{#if cardData}
	<article class="card glassStrong">
		<div class="top">
			{#if cardData.iconUrl}
				<img
					src={cardData.iconUrl}
					alt=""
					on:error={() => {
						if (cardData) cardData.iconUrl = "";
					}}
				/>
			{:else}
				<span class="fallback"><IconoirFileNotFound /></span>
			{/if}
			<span class="kind">{cardData.kind}</span>
		</div>

		<h3>
			<a href={cardData.url} target="_blank" rel="noopener noreferrer">
				{cardData.name}
			</a>
		</h3>

		<div class="meta">
			{#if cardData.fee !== "N/A"}
				<p><span>Fee</span> {cardData.fee}%</p>
				<p
					class="withHelp"
					title="If the fund is not 5 years old, the 1-year return is used instead"
				>
					<span><HelpIcon /> Avg / yr</span>
					{cardData.rate}%
				</p>
			{:else}
				<p><span>Rate</span> {cardData.rate}%</p>
			{/if}
		</div>
	</article>
{/if}

<style>
	.card {
		width: min(100%, 260px);
		border-radius: 18px;
		padding: 14px 14px 12px;
		text-align: left;
		display: flex;
		flex-direction: column;
		gap: 10px;
		animation: riseIn 0.35s ease both;
	}

	.top {
		display: flex;
		align-items: center;
		justify-content: space-between;
		gap: 8px;
	}

	img,
	.fallback {
		width: 40px;
		height: 40px;
		border-radius: 12px;
		object-fit: cover;
		background: rgba(255, 255, 255, 0.55);
		display: inline-flex;
		align-items: center;
		justify-content: center;
	}

	.kind {
		font-size: 11px;
		font-weight: 700;
		letter-spacing: 0.04em;
		text-transform: uppercase;
		color: var(--text);
		background: rgba(255, 255, 255, 0.45);
		border-radius: 999px;
		padding: 4px 8px;
	}

	h3 {
		margin: 0;
		font-size: 0.98rem;
		line-height: 1.3;
		font-weight: 700;
	}

	h3 a {
		color: var(--text-h);
		text-decoration: none;
	}

	h3 a:hover {
		color: var(--accent);
	}

	.meta {
		display: flex;
		flex-direction: column;
		gap: 4px;
	}

	.meta p {
		margin: 0;
		display: flex;
		justify-content: space-between;
		gap: 10px;
		font-size: 13px;
		font-weight: 650;
	}

	.meta span {
		color: var(--text);
		font-weight: 600;
		display: inline-flex;
		align-items: center;
		gap: 4px;
	}

	.withHelp span {
		cursor: help;
	}
</style>
