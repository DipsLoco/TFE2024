document.getElementById('draft-form').addEventListener('input', function() {
    const subject = document.getElementById('subject').value;
    const body = document.getElementById('body').value;
    const recipientId = document.querySelector('input[name="recipient_id"]').value;

    fetch('{% url "drafts" %}', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': '{{ csrf_token }}'
        },
        body: JSON.stringify({ subject, body, recipient_id: recipientId })
    });
});