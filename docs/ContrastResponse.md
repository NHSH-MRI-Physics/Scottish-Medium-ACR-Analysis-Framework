## Contrast Response Resolution

The contrast response considers the difference in signal between the bright spots and dark regions between them on the resolution block on the ACR phantom. 
<img width="1760" height="830" alt="image" src="https://github.com/user-attachments/assets/868ed691-acc1-420a-868d-82b5691bc903" />

The first stage is identifying the bright dots and dark region between them on each resolution block, this can be done manually or automated. The signal from the bright spots (Peaks) and from the dark regions between the bright spots (Troughs) is found. An amplitude is computed which equals the average peak signal minus the average trough signal. The resolution is computed by dividing the amplitude by the average peak signal. Meaning 100% resolution corepsonds to a average peak signal which goes from 0 intensity to max intensity. As resolution decreases the signal from the dark region will increase (and the signal from the bright decrease) as it smears out, this will result in a non-100% resolution. This is demonstrated in the below example. 

<img width="2400" height="3600" alt="image" src="https://github.com/user-attachments/assets/33947e44-3ae9-4d26-9cc0-3c4a089103c3" />
