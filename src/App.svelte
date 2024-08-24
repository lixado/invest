<script lang="ts">
  import svelteLogo from "./assets/svelte.svg";
    import CircleChooser from "./components/CircleChooser.svelte";
  import Curriculum from "./components/Curriculum.svelte";
    import JuliaSet from "./components/JuliaSet.svelte";
    import Mandelbrot from "./components/JuliaSet.svelte";
  import viteLogo from "/vite.svg";

  /*   let count = 0;
  
  function increment() {
    count += 1;
  } */
  function handleClick(){
    console.log("T");
  }
 
</script>

  <!--   <div>
    <a href="https://vitejs.dev" target="_blank" rel="noreferrer">
      <img src={viteLogo} class="logo" alt="Vite Logo" />
    </a>
    <a href="https://svelte.dev" target="_blank" rel="noreferrer">
      <img src={svelteLogo} class="logo svelte" alt="Svelte Logo" />
    </a>
  </div>

  {#if count < 10}
    <h1>My website!!!</h1>
  {/if}
  {#if count > 9}
    <Curriculum></Curriculum>
  {/if}

  <button on:click={increment}>
    Clicked {count}
    {count === 1 ? 'time' : 'times'}
  </button>
  

  <p>
    Check out <a href="https://github.com/sveltejs/kit#readme" target="_blank" rel="noreferrer">SvelteKit</a>, the official Svelte app framework powered by Vite!
  </p>

  <p class="read-the-docs">
    Click on the Vite and Svelte logos to learn more
  </p> -->

<main>
  <JuliaSet>

  </JuliaSet>
</main>

<style>

</style>
