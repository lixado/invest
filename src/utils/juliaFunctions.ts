function map(x_norm: number, min: number, max: number) {
    return min + (max - min) * x_norm;
}

function absComplex(z: Array<number>){ return Math.sqrt(z[0]*z[0] + z[1]*z[1]); }

function julia(x: number, y: number, width: number, height: number, c: number[], max_iterations: number, escape_radius: number, x_limits: number[], y_limits: number[]): number {
    let a = map(x/width, x_limits[0], x_limits[1]);
    let b = map(y/height, y_limits[0], y_limits[1]);
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

export { julia, getColorFromPalette, map };