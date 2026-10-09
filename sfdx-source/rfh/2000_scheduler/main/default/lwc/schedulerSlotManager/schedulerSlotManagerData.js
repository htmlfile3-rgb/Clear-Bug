// Data layer. Mock implementation so the UI runs standalone.
// Replace each function body with an imperative Apex call (see docs/appointment-slot-manager-design.md).
const TYPES = ['Academic Advising', 'Financial Aid Review', 'Admissions Interview'];
const DATES = ['Mon 12 Oct', 'Tue 13 Oct', 'Wed 14 Oct', 'Thu 15 Oct', 'Fri 16 Oct'];
const TIMES = ['09:00', '09:30', '10:00', '10:30', '11:00', '13:30', '14:00', '14:30', '15:00'];

let nextId = 3;
let appointments = [
    { id: '1', type: TYPES[0], date: 'Wed 14 Oct', time: '10:30' },
    { id: '2', type: TYPES[1], date: 'Fri 16 Oct', time: '14:00' }
];

const delay = (value) => new Promise((resolve) => setTimeout(() => resolve(value), 150));

export const appointmentTypes = TYPES;
export const dates = DATES;

export function getAppointments() {
    return delay(appointments.map((a) => ({ ...a })));
}

export function getSlots(date) {
    return delay(
        TIMES.map((time, i) => ({
            time,
            taken: (date.length + time.length * 3 + DATES.indexOf(date) * 2 + i) % 4 === 0
        }))
    );
}

export function bookAppointment(type, date, time) {
    appointments = [...appointments, { id: String(nextId++), type, date, time }];
    return delay();
}

export function transferAppointment(id, date, time) {
    appointments = appointments.map((a) => (a.id === id ? { ...a, date, time } : a));
    return delay();
}

export function cancelAppointment(id) {
    appointments = appointments.filter((a) => a.id !== id);
    return delay();
}
