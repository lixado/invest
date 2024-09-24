function formatNumber(value: string): string {
    return value.replace(/\D/g, '').replace(/\B(?=(\d{3})+(?!\d))/g, ',');
}

function formatCurrency(value: number): string {
    return new Intl.NumberFormat('no-NO', {
        style: 'currency',
        currency: 'NOK'
    }).format(value);
}

export { formatNumber, formatCurrency };