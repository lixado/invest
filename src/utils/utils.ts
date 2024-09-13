function formatNumber(value: string): string {
    return value.replace(/\D/g, '').replace(/\B(?=(\d{3})+(?!\d))/g, ',');
}

export { formatNumber };