<script lang="ts">
    import { onMount } from "svelte";

    // set limits on c
    const cMin = [-2, -2];
    const cMax = [2, 2];
    const max_iterations = 100; // Increased for better detail
    const escape_radius = 2; // Reduced to standard value
    const mouseEventsSkip = 10; // the lower the better FPS, but the lower the more cpu we use and might get laggy

    var c = [-1, 0]; // Changed to a more interesting starting point
    var currentMouseEvent = 0;
    var context: CanvasRenderingContext2D;

    function absComplex(z: Array<number>){ return Math.sqrt(z[0]*z[0] + z[1]*z[1]); }

    function map(x_norm: number, min: number, max: number) {
        return min + (max - min) * x_norm;
    }

    function julia(x: number, y: number, width: number, height: number): number {
        let a = map(x/width, -2, 2);
        let b = map(y/height, -2, 2);
        let z = [a, b];

        let i = 0;
        while (i < max_iterations) 
        {
            let aa = z[0]*z[0] - z[1]*z[1];
            let bb = 2*z[0]*z[1];
            z[0] = aa + c[0];
            z[1] = bb + c[1];
            
            if (absComplex(z) > escape_radius) return i;

            i += 1;
        }

        return i;
    }

    function getColorFromPalette(value: number): number[] {
        value = Math.max(0, Math.min(1, value));
        const r = Math.floor(255 * Math.sin(value * Math.PI));
        const g = Math.floor(255 * Math.sin(value * Math.PI * 2));
        const b = Math.floor(255 * Math.sin(value * Math.PI * 4));
        return [r, g, b];
    }

    function draw(event: MouseEvent) {
        if(currentMouseEvent < mouseEventsSkip)
        {
            currentMouseEvent += 1;
            return;
        }
        else { currentMouseEvent = 0; }

        const width = window.innerWidth;
        const height = window.innerHeight;
        context.clearRect(0, 0, width, height);

        let mousePosX = map(event.clientX/width, cMin[0], cMax[0]);
        let mousePosY = map(event.clientY/height, cMin[1], cMax[1]);

        c = [mousePosX, mousePosY];

        let img = context.createImageData(width, height);
        let img_data = new Uint32Array(img.data.buffer);

        for (let x = 0; x < width; x++) 
        {
            for (let y = 0; y < height; y++) 
            {
                let iterations = julia(x, y, width, height);
                const scaleIntensity = iterations / max_iterations;
                let rgb = getColorFromPalette(scaleIntensity);

                img_data[y * width + x] = (
                    (255 << 24) |    // alpha
                    (rgb[2] << 16) | // blue
                    (rgb[1] << 8) |  // green
                    rgb[0]           // red
                );
            }
        }

        context.putImageData(img, 0, 0);
    }

    onMount(() => {
        let canvas = <HTMLCanvasElement>document.getElementById("canvas");
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;

        context = canvas.getContext("2d") ?? new CanvasRenderingContext2D;
        context.imageSmoothingEnabled = false;

        draw(new MouseEvent('click')); // Initial draw
    });
</script>

<main>
    <canvas class="fillViewPort" id="canvas" on:mousemove={draw}></canvas>
</main>

<style>
    .fillViewPort {
        width: 100vw;
        height: 100vh;
        position: absolute;
        top: 0;
        left: 0;
    }
</style>
