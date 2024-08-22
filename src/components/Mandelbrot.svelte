<script lang="ts">
    import { onMount } from "svelte";

    const max_iterations = 25;
    const n = 2;
    const minCx = -1;
    const maxCx = 0.4;
    const minCy = -1;
    const maxCy = 1;
    const mouseEventsSkip = 5; // the lower the better FPS, but the lower the more cpu we use and might get laggy

    var c = [-1, 0]
    var R = (1 + Math.sqrt(1+4*abs(c))) / 2; // escape radius
    var currentMouseEvent = 0;
    var context: CanvasRenderingContext2D;

    function abs(z: Array<number>){  // absolute value of a complex number
        return Math.sqrt(z[0]*z[0] + z[1]*z[1]);
    }

    function julia(x: number, y: number, width: number, height: number): number {
        /* returns a number [0, 1] */

        let x1 = (R/width) * (2 * x - width);
        let y2 = (R/height) * (height - 2 * y);

        let z =  [x1, y2];

        let zs = [abs(z)];

        let i = 0;
        while (i < max_iterations) 
        {
            z = [z[0]*z[0] - z[1] * z[1] + c[0], 2 * z[0] * z[1] + c[1]];
            if (abs(z) > R) return 0;

            zs.push(abs(z));

            i += 1;
        }

        return zs.reduce((a, b) => a + b, 0) / zs.length;
    }

    function toHex( val: number ) {
      return  Math.round( val * 255 ).toString(16);
    }

    function draw(event: MouseEvent) {
        if(currentMouseEvent < mouseEventsSkip)
        {
            currentMouseEvent += 1;
            return;
        }
        else { currentMouseEvent = 0; }

        // get dims
        const width = window.innerWidth;
        const height = window.innerHeight;

        // clear
        context.clearRect(0, 0, width, height);

        // transform it to [minCx, maxCx]
        let mousePosX = minCx + (maxCx - minCx)*(event.clientX/width);
        let mousePosY = minCy + (maxCy - minCy)*(event.clientY/height);

        c = [mousePosX, mousePosY];
        R = (1 + Math.sqrt(1+4*abs(c))) / 2;

        let img = new ImageData( width, height );
        let img_data = new Uint32Array( img.data.buffer );

        for (let x = 0; x <= width; x++) 
        {
            for (let y = 0; y <= height; y++) 
            {
                const scale = (1/7);
                let avg_growth = julia(x, y, width*scale, height*scale); // moving it into place

                if(avg_growth > 0)
                {
                    const scaleIntensity = Math.exp(avg_growth / (R)) - 1;
                    const colorIntensity = Math.round(scaleIntensity * 255);

                    let rgbNumber = Number( '0xFF' + toHex(colorIntensity) + toHex(0) + toHex(0) ); // we want 0xAABBGGRR format

                    if(scaleIntensity > 0.4) rgbNumber = Number( '0xFF' + toHex(0) + toHex(colorIntensity) + toHex(0) );
                    
                    img_data[ y * width + x] = rgbNumber; // save to buffer
                }
                else
                {
                    img_data[ y * width + x] = Number( '0xFF' + toHex(0) + toHex(0) + toHex(0) ); // black pixel
                }
            }
        }

        // draw now everything at same time
        context.putImageData(img, 0, 0 );
    }

    onMount(() => {
        let canvas = <HTMLCanvasElement>document.getElementById("canvas");

        context = canvas.getContext("2d") ?? new CanvasRenderingContext2D;
        context.imageSmoothingEnabled = true;
        context.imageSmoothingQuality = "high";
    });
</script>

<main>
    <canvas class="fillViewPort" id="canvas" on:mousemove={draw}></canvas>
</main>

<style>
    .fillViewPort {
        /*make full screen*/
        /* background-color: aqua; */
        width: 100vw; /* Use 'v' for viewport units */
        height: 100vh; /* Use 'h' for height unit in viewport context */
        position: absolute; /* Position the element absolutely to cover the whole screen */
        top: 0; /* Set the top margin to zero */
        left: 0; /* Set the left margin to zero */
    }
</style>
