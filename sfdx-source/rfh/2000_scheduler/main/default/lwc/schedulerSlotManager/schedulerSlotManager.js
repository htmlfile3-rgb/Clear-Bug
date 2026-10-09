import { LightningElement, api } from 'lwc';
import {
    appointmentTypes,
    dates,
    getAppointments,
    getSlots,
    bookAppointment,
    transferAppointment,
    cancelAppointment
} from './schedulerSlotManagerData';

const TITLES = { book: 'Book appointment', transfer: 'Transfer appointment', cancel: 'Cancel appointment' };

export default class SchedulerSlotManager extends LightningElement {
    @api resourceGroupName = 'Student Success Advising';
    @api resourceGroupSummary = '3 advisors · Mon–Fri, 09:00–16:00 · Main Campus and Online';

    appointments = [];
    slots = [];
    message = '';
    errorMessage = '';
    isLoading = true;
    isSaving = false;

    mode; // 'book' | 'transfer' | 'cancel' | undefined
    target; // appointment being transferred / cancelled
    selectedType = appointmentTypes[0];
    selectedDate = dates[0];
    selectedTime;

    connectedCallback() {
        this.loadAppointments();
    }

    async loadAppointments() {
        this.isLoading = true;
        try {
            this.appointments = await getAppointments();
        } catch (e) {
            this.errorMessage = 'We could not load your appointments. Refresh the page and try again.';
        } finally {
            this.isLoading = false;
        }
    }

    get typeOptions() {
        return appointmentTypes.map((t) => ({ label: t, value: t }));
    }
    get dateOptions() {
        return dates.map((d) => ({ label: d, value: d }));
    }
    get hasAppointments() {
        return this.appointments.length > 0;
    }
    get isDialogOpen() {
        return !!this.mode;
    }
    get isBook() {
        return this.mode === 'book';
    }
    get isTransfer() {
        return this.mode === 'transfer';
    }
    get isCancel() {
        return this.mode === 'cancel';
    }
    get showPicker() {
        return this.isBook || this.isTransfer;
    }
    get dialogTitle() {
        return TITLES[this.mode];
    }
    get confirmLabel() {
        return this.isCancel ? 'Cancel appointment' : 'Confirm';
    }
    get closeLabel() {
        return this.isCancel ? 'Keep' : 'Close';
    }
    get confirmVariant() {
        return this.isCancel ? 'destructive' : 'brand';
    }
    get confirmDisabled() {
        return this.isSaving || (this.showPicker && !this.selectedTime);
    }
    get currentSummary() {
        return this.target ? `${this.target.type}, ${this.target.date} at ${this.target.time}` : '';
    }
    get slotItems() {
        return this.slots.map((s) => ({
            ...s,
            key: s.time,
            selected: s.time === this.selectedTime,
            className: 'slot-button' + (s.time === this.selectedTime ? ' slot-button_selected' : ''),
            ariaPressed: String(s.time === this.selectedTime),
            title: s.taken ? 'Unavailable' : ''
        }));
    }

    // Actions
    handleBook() {
        this.openDialog('book');
    }
    handleTransfer(event) {
        this.openDialog('transfer', event.currentTarget.dataset.id);
    }
    handleCancel(event) {
        this.openDialog('cancel', event.currentTarget.dataset.id);
    }

    async openDialog(mode, id) {
        this.target = id ? this.appointments.find((a) => a.id === id) : undefined;
        this.mode = mode;
        this.selectedTime = undefined;
        this.errorMessage = '';
        this.message = '';
        if (mode === 'book') {
            this.selectedType = appointmentTypes[0];
        }
        if (mode !== 'cancel') {
            await this.loadSlots();
        }
    }

    async loadSlots() {
        this.slots = await getSlots(this.selectedDate);
    }

    handleTypeChange(event) {
        this.selectedType = event.detail.value;
    }
    async handleDateChange(event) {
        this.selectedDate = event.detail.value;
        this.selectedTime = undefined;
        await this.loadSlots();
    }
    handleSlotClick(event) {
        this.selectedTime = event.currentTarget.dataset.time;
    }

    handleClose() {
        this.mode = undefined;
        this.target = undefined;
    }
    handleKeydown(event) {
        if (event.key === 'Escape') {
            this.handleClose();
        }
    }

    async handleConfirm() {
        this.isSaving = true;
        this.errorMessage = '';
        try {
            if (this.isBook) {
                await bookAppointment(this.selectedType, this.selectedDate, this.selectedTime);
                this.message = 'Appointment booked.';
            } else if (this.isTransfer) {
                await transferAppointment(this.target.id, this.selectedDate, this.selectedTime);
                this.message = 'Appointment moved.';
            } else {
                await cancelAppointment(this.target.id);
                this.message = 'Appointment cancelled.';
            }
            this.handleClose();
            await this.loadAppointments();
        } catch (e) {
            // Typical cause: the slot was taken by someone else. Keep the dialog open and refresh times.
            this.errorMessage = 'That change could not be saved. Choose another time and try again.';
            if (this.showPicker) {
                await this.loadSlots();
                this.selectedTime = undefined;
            }
        } finally {
            this.isSaving = false;
        }
    }
}
