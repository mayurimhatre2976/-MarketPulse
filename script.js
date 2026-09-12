// MarketPulse - Interactive Frontend Logic

document.addEventListener('DOMContentLoaded', () => {
  // 1. Live Table Search & Filter
  const tableSearchInput = document.getElementById('tableSearch');
  const statusFilterSelect = document.getElementById('statusFilter');
  const dataTable = document.querySelector('.table-filterable');

  function filterTable() {
    if (!dataTable) return;
    const searchTerm = tableSearchInput ? tableSearchInput.value.toLowerCase().trim() : '';
    const selectedStatus = statusFilterSelect ? statusFilterSelect.value.toLowerCase().trim() : 'all';

    const rows = dataTable.querySelectorAll('tbody tr:not(.empty-row)');
    let visibleCount = 0;

    rows.forEach(row => {
      const rowText = row.innerText.toLowerCase();
      const statusCell = row.getAttribute('data-status') || '';
      
      const matchesSearch = searchTerm === '' || rowText.includes(searchTerm);
      const matchesStatus = selectedStatus === 'all' || selectedStatus === '' || statusCell.toLowerCase() === selectedStatus;

      if (matchesSearch && matchesStatus) {
        row.style.display = '';
        visibleCount++;
      } else {
        row.style.display = 'none';
      }
    });

    // Check if an empty state notice should be displayed
    let emptyRow = dataTable.querySelector('.empty-row');
    if (visibleCount === 0) {
      if (!emptyRow) {
        emptyRow = document.createElement('tr');
        emptyRow.className = 'empty-row';
        const colCount = dataTable.querySelectorAll('thead th').length || 6;
        emptyRow.innerHTML = `<td colspan="${colCount}" class="text-center text-muted py-4"><i class="bi bi-search me-2"></i>No matching records found.</td>`;
        dataTable.querySelector('tbody').appendChild(emptyRow);
      } else {
        emptyRow.style.display = '';
      }
    } else if (emptyRow) {
      emptyRow.style.display = 'none';
    }
  }

  if (tableSearchInput) {
    tableSearchInput.addEventListener('input', filterTable);
  }
  if (statusFilterSelect) {
    statusFilterSelect.addEventListener('change', filterTable);
  }

  // 2. Dynamic Coupon Validation on Purchase Modal
  const validateCouponBtn = document.getElementById('btnValidateCoupon');
  const couponInput = document.getElementById('purchaseCouponCode');
  const amountInput = document.getElementById('purchaseAmount');
  const couponFeedback = document.getElementById('couponFeedback');
  const finalAmountDisplay = document.getElementById('finalAmountDisplay');
  const estimatedPointsDisplay = document.getElementById('estimatedPointsDisplay');

  function calculatePointsLocal(amount) {
    return Math.floor(amount * 0.1);
  }

  if (amountInput) {
    amountInput.addEventListener('input', () => {
      const amt = parseFloat(amountInput.value) || 0;
      if (finalAmountDisplay && (!couponInput || !couponInput.value.trim())) {
        finalAmountDisplay.textContent = amt.toFixed(2);
        if (estimatedPointsDisplay) {
          estimatedPointsDisplay.textContent = calculatePointsLocal(amt);
        }
      }
    });
  }

  if (validateCouponBtn && couponInput) {
    validateCouponBtn.addEventListener('click', async () => {
      const code = couponInput.value.trim();
      const amount = parseFloat(amountInput ? amountInput.value : 0) || 0;

      if (!code) {
        couponFeedback.innerHTML = '<span class="text-muted">Enter a coupon code to validate.</span>';
        return;
      }

      try {
        couponFeedback.innerHTML = '<span class="text-primary"><i class="bi bi-arrow-repeat spin me-1"></i> Checking coupon...</span>';
        const response = await fetch('/api/validate-coupon', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ code, amount })
        });
        const data = await response.json();

        if (data.valid) {
          couponFeedback.innerHTML = `<span class="text-success fw-bold"><i class="bi bi-check-circle-fill me-1"></i> ${data.message}</span>`;
          if (finalAmountDisplay) {
            finalAmountDisplay.textContent = parseFloat(data.final_amount).toFixed(2);
          }
          if (estimatedPointsDisplay) {
            estimatedPointsDisplay.textContent = data.estimated_points;
          }
        } else {
          couponFeedback.innerHTML = `<span class="text-danger"><i class="bi bi-x-circle-fill me-1"></i> ${data.message}</span>`;
          if (finalAmountDisplay) {
            finalAmountDisplay.textContent = amount.toFixed(2);
          }
          if (estimatedPointsDisplay) {
            estimatedPointsDisplay.textContent = calculatePointsLocal(amount);
          }
        }
      } catch (err) {
        couponFeedback.innerHTML = '<span class="text-danger">Failed to validate coupon code.</span>';
      }
    });
  }

  // 3. One-Click Copy Coupon Code
  document.querySelectorAll('.btn-copy-code').forEach(button => {
    button.addEventListener('click', (e) => {
      e.preventDefault();
      const code = button.getAttribute('data-code');
      if (code) {
        navigator.clipboard.writeText(code).then(() => {
          const originalHtml = button.innerHTML;
          button.innerHTML = '<i class="bi bi-check-lg text-success"></i> Copied!';
          button.classList.add('btn-light');
          setTimeout(() => {
            button.innerHTML = originalHtml;
            button.classList.remove('btn-light');
          }, 2000);
        });
      }
    });
  });

  // 4. Auto-dismiss alerts after 5 seconds
  const autoAlerts = document.querySelectorAll('.alert-dismissible');
  autoAlerts.forEach(alert => {
    setTimeout(() => {
      const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
      if (bsAlert) bsAlert.close();
    }, 5000);
  });
});
