import { getColorFromPalette, julia } from './juliaFunctions';

self.onmessage = (e) => {
  const { x, y, width, height, c, max_iterations, escape_radius, x_limits, y_limits } = e.data; // this is input
  const iterations = julia(x, y, width, height, c, max_iterations, escape_radius, x_limits, y_limits);
  const scaleIntensity = iterations / max_iterations;
  const rgb = getColorFromPalette(scaleIntensity);
  
  self.postMessage({ x, y, rgb }); // output
};