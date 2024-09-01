<script lang="ts">
  import CircleChooser from "./components/CircleChooser.svelte";
  import Curriculum from "./components/Curriculum.svelte";
  import FundVsBankCalculator from "./components/FundVsBankCalculator.svelte";
  import JuliaSet from "./components/JuliaSet.svelte";


  let id = 0;

  function handleClick(x: number){
    id = x;
  }

  let juliaSetComponent: JuliaSet;
</script>


<main on:mousemove={(e) => juliaSetComponent != null ? juliaSetComponent.draw(e) : null}>
  <div class="centerButtons">
    <button on:click={() => handleClick(1)}>
      Julia Set
    </button>
    <button on:click={() => handleClick(2)}>
      CV
    </button>
    <button on:click={() => handleClick(3)}>
      Fund VS Bank calculator
    </button>
  </div>

  {#if id == 1}
    <br>
    <div class="fullscreen">
      <JuliaSet bind:this={juliaSetComponent}/>
    </div>
  {/if}
  {#if id == 2}
    <br>
    <Curriculum />
  {/if}
  {#if id == 3}
    <br>
    <FundVsBankCalculator />
  {/if}
</main>

<style>
  .centerButtons{
    display: flex;
    justify-content: center; /* Center horizontally */
    align-items: center;     /* Center vertically */
    gap: 0.5em;
  }

  .fullscreen{
    width: 80vw;
    height: 80vh;
  }
</style>
