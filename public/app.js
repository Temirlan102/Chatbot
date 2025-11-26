const tg = window.Telegram.WebApp;
tg.ready();

let userId = tg.initDataUnsafe.user.id;
let slots = [];
let bookedSlotId = null;

async function loadSlots() {
  try {
    const res = await fetch("https://chatbot-snowy-psi.vercel.app/api/slots");
    slots = await res.json();

    const userRes = await fetch(
      `https://chatbot-snowy-psi.vercel.app/api/myappointment?user=${userId}`
    );
    const userData = await userRes.json();
    bookedSlotId = userData.appointment ? userData.appointment.id : null;

    const container = document.getElementById("slots-container");
    container.innerHTML = "";

    slots.forEach((slot) => {
      const btn = document.createElement("button");
      btn.textContent = `${slot.date} ${slot.time}`;

      if (slot.user) {
        btn.classList.add("booked");
        btn.disabled = true;
      } else if (slot.id === bookedSlotId) {
        btn.classList.add("selected");
      }

      btn.onclick = () => bookSlot(slot.id);
      container.appendChild(btn);
    });
  } catch (err) {
    console.error(err);
    document.getElementById("slots-container").textContent =
      "Failed to load slots.";
  }
}

async function bookSlot(slotId) {
  try {
    const res = await fetch("https://chatbot-snowy-psi.vercel.app/api/book", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ slotId, user: userId }),
    });

    const data = await res.json();
    if (res.ok) {
      alert(`🎉 ${data.message}`);
    } else {
      alert(`❌ ${data.error}`);
    }

    loadSlots();
  } catch (err) {
    console.error(err);
    alert("Failed to book slot");
  }
}

window.onload = loadSlots;
