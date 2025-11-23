const express = require("express");
const cors = require("cors");
const fs = require("fs");
const path = require("path");

const app = express();
app.use(express.json());
app.use(cors());

const DATA_FILE = path.join(__dirname, "appointments.json");

function loadData() {
  return JSON.parse(fs.readFileSync(DATA_FILE, "utf8"));
}

function saveData(data) {
  fs.writeFileSync(DATA_FILE, JSON.stringify(data, null, 2));
}

app.get("/slots", (req, res) => {
  const data = loadData();
  res.json(data.availableSlots);
});

app.post("/book", (req, res) => {
  const { slotId, user } = req.body;
  const data = loadData();

  const slot = data.availableSlots.find((s) => s.id === slotId);
  if (!slot) return res.status(400).json({ error: "Slot not available" });

  data.bookedSlots.push({ ...slot, user });
  data.availableSlots = data.availableSlots.filter((s) => s.id !== slotId);

  saveData(data);
  res.json({ message: "Appointment booked!", slot });
});

app.get("/myappointment", (req, res) => {
  const { user } = req.query;
  const data = loadData();

  const booking = data.bookedSlots.find((b) => b.user === user);

  if (!booking) return res.json({ message: "No appointment found" });

  res.json({ appointment: booking });
});

app.post("/edit", (req, res) => {
  const { user, newSlotId } = req.body;
  const data = loadData();

  const currentIndex = data.bookedSlots.findIndex((b) => b.user === user);
  if (currentIndex === -1)
    return res.status(400).json({ error: "No current booking" });

  const newSlot = data.availableSlots.find((s) => s.id === newSlotId);
  if (!newSlot)
    return res.status(400).json({ error: "New slot not available" });

  const oldBooking = data.bookedSlots[currentIndex];

  data.availableSlots.push({
    id: oldBooking.id,
    date: oldBooking.date,
    time: oldBooking.time,
  });

  data.bookedSlots[currentIndex] = { ...newSlot, user };
  data.availableSlots = data.availableSlots.filter((s) => s.id !== newSlotId);

  saveData(data);
  res.json({
    message: "Appointment updated!",
    appointment: data.bookedSlots[currentIndex],
  });
});

app.get("/health", (req, res) => res.json({ status: "ok" }));
app.use(express.static(path.join(__dirname, "public")));

app.listen(3000, () => console.log("Backend running at http://localhost:3000"));
