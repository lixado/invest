<script lang="ts">
    import { createEventDispatcher } from "svelte";
    import { slide, scale } from "svelte/transition";
    import { formatNumber } from "../utils/utils";

    import LucideSidebarOpen from "virtual:icons/lucide/sidebar-open";
    import AddIcon from "virtual:icons/lucide/plus";
    import AutocompleteSelector from "./AutocompleteSelector.svelte";

    const dispatch = createEventDispatcher();

    export let startAmount: number = 10000;
    export let monthlyContribution: number = 1000;

    let startAmountInput: string = formatNumber(startAmount.toString());
    let monthlyContributionInput: string = formatNumber(
        monthlyContribution.toString(),
    );

    var showAddFundInput = false;
    var showAddBankInput = false;

    function addFund() {
        showAddFundInput = true;
    }

    function addBank() {
        dispatch("addBank");
    }

    function resetZoom() {
        dispatch("resetZoom");
    }

    function change() {
        startAmount = Number(startAmountInput.replace(/,/g, ""));
        monthlyContribution = Number(
            monthlyContributionInput.replace(/,/g, ""),
        );
        dispatch("change");
    }

    function closeSidebar() {
        dispatch("close");
    }
</script>

<main class="sidebar" transition:slide={{ duration: 300, axis: "x" }}>
    <button class="close-button" on:click={closeSidebar}
        ><LucideSidebarOpen style="rotate: 180deg;" /></button
    >

    <div class="sidebar-content">
        <button on:click={resetZoom}>Reset Zoom</button>
        <br />

        <div>
            <label for="startAmount">Start Amount:</label>
            <input
                style="width: 60%; text-align: right;"
                type="text"
                id="startAmount"
                bind:value={startAmountInput}
                placeholder="Enter starting amount"
                on:input={(e) => {
                    startAmountInput = formatNumber(e.currentTarget.value);
                    change();
                }}
            />
        </div>

        <div>
            <label for="monthlyContribution">Monthly Contribution:</label>
            <input
                style="width: 60%; text-align: right;"
                type="text"
                id="monthlyContribution"
                bind:value={monthlyContributionInput}
                placeholder="Enter monthly contribution"
                on:input={(e) => {
                    monthlyContributionInput = formatNumber(
                        e.currentTarget.value,
                    );
                    change();
                }}
            />
        </div>

        <div
            style="display: flex; align-items: center; justify-content: center; gap: 0.5em;white-space: nowrap;"
        >
            {#if showAddFundInput}
                <div transition:slide={{ duration: 75, axis: "x" }}>
                    <AutocompleteSelector />
                </div>
            {:else}
                <button on:click={addFund}>
                    <AddIcon /> Add Fund
                </button>
            {/if}
        </div>

        <button
            style="display: flex; align-items: center; gap: 0.5em;white-space: nowrap;"
            on:click={addBank}
        >
            <AddIcon /> Add Bank
        </button>
    </div>
</main>

<style>
    .close-button {
        position: absolute;
        top: 50%;
        right: -75px; /* Adjust this value to position the button outside the sidebar */
        transform: translateY(-50%);
        z-index: 1000;
    }
    .sidebar-content {
        display: flex;
        gap: 1em;
        flex-direction: column;
        justify-content: center;
        height: 100%;
    }

    .sidebar {
        position: fixed;
        left: 0;
        top: 0;
        bottom: 0;
        width: 250px;
        padding: 1rem;
        background-color: #242424;
        box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
        border-right: 1px solid #ccc;
        z-index: 10; /* Add this line to ensure the sidebar appears above other elements */
    }

    .input-group {
        margin-top: 1rem;
        margin-right: 1rem;
    }

    label {
        display: block;
        margin-bottom: 0.5rem;
    }

    input {
        width: 100%;
        padding: 0.5rem;
    }
</style>
