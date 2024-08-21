<script lang="ts">
    const max_iterations = 1000;
    const n = 2;
    const c = [-1, 0]
    const R = (1 + Math.sqrt(1+4*abs(c))) / 2; // escape radius choose R > 0 such that R**n - R >= sqrt(cx**2 + cy**2)

    function conversion(x, y, width){   // transformation from canvas coordinates to XY plane
        var m = R / width;
        var x1 = m * (2 * x - width);
        var y2 = m * (width - 2 * y);
        return [x1, y2];
    }

    function f(z, c){  // calculate the value of the function with complex arguments.
        return [z[0]*z[0] - z[1] * z[1] + c[0], 2 * z[0] * z[1] + c[1]];
    }

    function abs(z){  // absolute value of a complex number
        return Math.sqrt(z[0]*z[0] + z[1]*z[1]);
    }

    function julia(x_norm: number, y_norm: number): number {
        /* returns
         */
        //const randomNumber = Math.round(Math.random());
        //return randomNumber;
        
        // (scale to be between -R and R)

        return i;
    }

    function draw(event: Event) {
        let canvas = document.getElementById("canvas");
        let ctx = canvas.getContext("2d");

        ctx.clearRect(0, 0, canvas.width, canvas.height);
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        console.log(ctx);
        //console.log(R**n - R >= Math.sqrt(cx**2 + cy**2)); // this must be true see up
        console.log(event.clientX)
        console.log(event.clientY)

        // scale them down
        let mousePosX = 0;
        let mousePosY = 0.5;

        for (let x = 0; x <= canvas.width; x++) {
            for (let y = 0; y <= canvas.height; y++) {
                let z = conversion(x, y, canvas.width);
                let flag = true;
                for (var i = 0; i < max_iterations; i++){ // I know I can change it to while and remove this flag.
                    z = f(z, c);
                    if (abs(z) > R){  // if during every one of the iterations we have value bigger then R, do not draw this point.
                        flag = false;
                        break;
                    }
                }
                //const result = julia(x/canvas.width, y/canvas.height);

                //const blueIntensity = Math.round((result / max_iterations) * 255);
                if(flag)
                {
                    ctx.fillStyle = `rgb(0, 0, 125)`;
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
