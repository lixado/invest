<script lang="ts">
import type { FundResult, Bank } from '../utils/models';
import AddIcon from "virtual:icons/material-symbols/add";
import IconoirFileNotFound from 'virtual:icons/iconoir/file-not-found';

export let fund: FundResult | null = null;
export let bank: Bank | null = null;

$: cardData = fund 
    ? {
        name: fund.instrument_info.name,
        iconUrl: fund.instrument_info.instrument_icon_url,
        rate: fund.historical_returns_info.yield_5y ? (Number(fund.historical_returns_info.yield_5y.toFixed(2)) / 5).toFixed(2) : 'N/A',
        fee: fund.fund_info.fund_calculated_fee?.toFixed(2) ?? 'N/A',
        url: `https://www.nordnet.no/market/funds?sortField=yield_1y&sortOrder=descending&freeTextSearch=${fund.instrument_info.name}`
    }
    : bank
    ? {
        name: bank.leverandorVisningsnavn + ` (${bank.navn})`,
        iconUrl: bank.leverandorUrl.endsWith('/') ? bank.leverandorUrl + 'favicon.ico' : bank.leverandorUrl + '/favicon.ico',
        rate: Number(bank.rentesats1)?.toFixed(2) ?? 'N/A',
        fee: 'N/A',
        url: bank.leverandorUrl
    }
    : null;

</script>


<main>
    {#if cardData}
        <div class="mat-card">
            {#if cardData.iconUrl}
                <img src={cardData.iconUrl} alt="Icon" style="width: 50px; height: 50px;" on:error={() => {cardData.iconUrl = '';}} />
            {:else}
                <IconoirFileNotFound style="width: 50px; height: 50px;"/>
            {/if}
            <h3>
                <a href={cardData.url} 
                    target="_blank">
                    {#if cardData.name.length > 20}
                        {cardData.name.slice(0, 20)}<br>
                        {cardData.name.slice(20)}
                    {:else}
                        {cardData.name}
                    {/if}
                </a>
            </h3>
            {#if cardData.fee !== 'N/A'}
                <p>Calculated Fee: {cardData.fee} %</p>
                <p>Avg 1 Year Increase(from last 5 years): {cardData.rate}%</p>
            {:else}
                <p>Last 1 Year Increase: {cardData.rate}%</p>
            {/if}
        </div>
    {/if}
</main>

<style>

</style>