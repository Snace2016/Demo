(function () {
    const searchInput = document.getElementById('search-input');
    const sortField = document.getElementById('sort-field');
    const discountFilter = document.getElementById('discount-filter');
    const table = document.getElementById('product-table');
    const tbody = table.querySelector('tbody');

    function getRows() {
        return Array.from(tbody.querySelectorAll('.product-row'));
    }

    function matchesDiscount(discount, range) {
        const d = parseFloat(discount);
        if (range === 'all') return true;
        if (range === '0-10.99') return d >= 0 && d <= 10.99;
        if (range === '11-14.99') return d >= 11 && d <= 14.99;
        if (range === '15+') return d >= 15;
        return true;
    }

    function matchesSearch(row, query) {
        if (!query) return true;
        const fields = [
            row.dataset.name,
            row.dataset.category,
            row.dataset.description,
            row.dataset.manufacturer,
            row.dataset.supplier,
            row.dataset.article,
            row.dataset.unit,
        ];
        return fields.some(function (f) {
            return f && f.includes(query);
        });
    }

    function applyFilters() {
        const query = (searchInput.value || '').toLowerCase().trim();
        const discountRange = discountFilter.value;
        const sort = sortField.value;

        let rows = getRows();

        rows.forEach(function (row) {
            const visible = matchesSearch(row, query) &&
                matchesDiscount(row.dataset.discount, discountRange);
            row.style.display = visible ? '' : 'none';
        });

        rows = rows.filter(function (row) {
            return row.style.display !== 'none';
        });

        if (sort) {
            const parts = sort.split('-');
            const field = parts[0];
            const dir = parts[1] === 'asc' ? 1 : -1;
            rows.sort(function (a, b) {
                const va = parseFloat(a.dataset[field]);
                const vb = parseFloat(b.dataset[field]);
                return (va - vb) * dir;
            });
        }

        rows.forEach(function (row) {
            tbody.appendChild(row);
        });
    }

    searchInput.addEventListener('input', applyFilters);
    sortField.addEventListener('change', applyFilters);
    discountFilter.addEventListener('change', applyFilters);
})();
