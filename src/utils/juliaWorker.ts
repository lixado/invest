import { getColorFromPalette, julia } from './juliaFunctions';

self.onmessage = (e) => {
  const { start_buffer_index, end_buffer_index, width, height, c, max_iterations, escape_radius, x_limits, y_limits } = e.data; // this is input

  var resultArr: Uint32Array = new Uint32Array(end_buffer_index - start_buffer_index); 

  for (let i = start_buffer_index; i < end_buffer_index; i++) {
    const x = i % width;
    const y = Math.floor(i / width);
    const iterations = julia(x, y, width, height, c, max_iterations, escape_radius, x_limits, y_limits);

    const scaleIntensity = iterations / max_iterations;
    const rgb = getColorFromPalette(scaleIntensity);

    const coloring = rgb[0] === 0 && rgb[1] === 0 && rgb[2] === 0 ? ( // insted of black, make it background color
      (255 << 24) |    // alpha
        (36 << 16) | // blue
        (36 << 8) |  // green
        36           // red
    ) : (
        (255 << 24) |    // alpha
        (rgb[2] << 16) | // blue
        (rgb[1] << 8) |  // green
        rgb[0]           // red
    );

    resultArr[i-start_buffer_index] = coloring;
  }



  self.postMessage({start_buffer_index, resultArr}); // output
};