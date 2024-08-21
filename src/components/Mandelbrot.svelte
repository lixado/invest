<script lang="ts">
    const max_iterations = 100;
    const n = 2;
    const c = [-1, 0]
    const R = (1 + Math.sqrt(1+4*abs(c))) / 2; // escape radius choose R > 0 such that R**n - R >= sqrt(cx**2 + cy**2)

    function abs(z){  // absolute value of a complex number
        return Math.sqrt(z[0]*z[0] + z[1]*z[1]);
    }

    function julia(x: number, y: number, width: number, height: number): number {
        /* returns a number [0, R] */

        let m = R / width;
        let x1 = m * (2 * x - width);
        let y2 = m * (height - 2 * y);

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

    function draw(event: Event) {
        console.log({R})
        let canvas = document.getElementById("canvas");
        let ctx = canvas.getContext("2d");

        ctx.clearRect(0, 0, canvas.width, canvas.height);

        let mousePosX = event.clientX;
        let mousePosY = event.clientY;

        for (let x = 0; x <= canvas.width; x++) {
            for (let y = 0; y <= canvas.height; y++) {
                let avg_growth = julia(x, y, canvas.width, canvas.height);

                //const blueIntensity = Math.round((result / max_iterations) * 255);
                if(avg_growth > 0)
                {
                    const scaleIntensity = Math.exp(avg_growth / R) - 1;
                    const colorIntensity = Math.round(scaleIntensity * 255);
                    console.log({scaleIntensity});
                    if(scaleIntensity > 0.4)
                        ctx.fillStyle = `rgb(0, ${colorIntensity}, 0)`;
                    else{
                        ctx.fillStyle = `rgb(0, 0, ${colorIntensity})`;
                    }
                    ctx.fillRect(x, y, 1, 1);
                }
            }
        }
    }
</script>

<main>
    <canvas class="fillViewPort" id="canvas" on:click={draw}></canvas>
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
