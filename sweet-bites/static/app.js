document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('.add-btn').forEach(btn => {
    btn.addEventListener('click', async (e) => {
      const id = btn.dataset.id;
      try {
        const res = await fetch(`/add_to_cart/${id}`, { method: 'POST' });
        if (!res.ok) throw new Error('Failed');
        const data = await res.json();
        if (data.cart_count !== undefined) {
          const el = document.getElementById('cart-count');
          if (el) el.textContent = data.cart_count;
          btn.textContent = 'Added';
          setTimeout(()=> btn.textContent = 'Add to cart', 900);
        }
      } catch (err) {
        alert('Could not add to cart right now.');
      }
    });
  });
});
