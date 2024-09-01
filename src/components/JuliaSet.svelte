<script lang="ts">
    import { onMount } from "svelte";
    import { map } from "../utils/juliaFunctions";
    import JuliaWorker from "../utils/juliaWorker.ts?worker";

    // set limits on c for Z = Z**2 + C
    const cMin = [-2, -2];
    const cMax = [2, 2];
    // set limits on rendering
    const x_limits = [-2, 2]; // limit on Re axis
    const y_limits = [-2, 2]; // limit on Im axis
    const max_iterations = 100; // Increased for better detail
    const escape_radius = 2; // Reduced to standard value
    const mouseEventsSkip = 8; // the lower the better FPS, but the lower the more cpu we use and might get laggy could change this to work based on fps

    var c = [-1, 0]; // Changed to a more interesting starting point
    var currentMouseEvent = 0;
    var context: CanvasRenderingContext2D;
    let workers: Worker[] = [];
    const numWorkers = navigator.hardwareConcurrency || 4;

    export function draw(event: MouseEvent) {
        if (currentMouseEvent < mouseEventsSkip) {
            currentMouseEvent += 1;
            return;
        } else {
            currentMouseEvent = 0;
        }

        console.log(event);

        const width = context.canvas.width;
        const height = context.canvas.height;

        const windowWidth = window.outerWidth;
        const windowHeight = window.outerHeight;

        let mousePosX = map(event.clientX / windowWidth, cMin[0], cMax[0]);
        let mousePosY = map(event.clientY / windowHeight, cMin[1], cMax[1]);

        c = [mousePosX, mousePosY];

        let img = context.createImageData(width, height);
        let img_data = new Uint32Array(img.data.buffer);

        const buffer_size = width * height;
        const chunkSize = Math.ceil(buffer_size / numWorkers);

        for (let i = 0; i < numWorkers; i++) {
            const start_buffer_index = i * chunkSize;
            const end_buffer_index = Math.min(start_buffer_index + chunkSize, buffer_size); // cant go over buffer

            workers[i].postMessage({
                start_buffer_index,
                end_buffer_index,
                width,
                height,
                c,
                max_iterations,
                escape_radius,
                x_limits,
                y_limits
            });
        }

        var completedChunks = 0;
        workers.forEach((worker, index) => {
            worker.onmessage = (e) => {
                const { start_buffer_index, resultArr } = e.data;
                img_data.set(resultArr, start_buffer_index);
                completedChunks++;

                if (completedChunks === numWorkers) {
                    context.putImageData(img, 0, 0);
                }
            };
        });
    }

    onMount(() => {
        let canvas = <HTMLCanvasElement>document.getElementById("canvas");
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;

        context = canvas.getContext("2d") ?? new CanvasRenderingContext2D();
        context.imageSmoothingEnabled = false;

        for (let i = 0; i < numWorkers; i++) {
            workers.push(new JuliaWorker());
        }

        draw(new MouseEvent("click")); // Initial draw
    });
    
</script>

<main>
    <canvas id="canvas"></canvas>
</main>

<style>
    canvas{
        display: flex;
        width: 100%;
        height: 100%;
    }
</style>
