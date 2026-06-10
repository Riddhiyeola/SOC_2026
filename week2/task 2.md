## Task 2: Analyze the Model

* **Input to the update network:** Calculates a perception vector using three fixed 3x3 convolutional filters (Identity, Sobel X, Sobel Y), expanding $C$ channels to $3C$ channels.
* **Output of the update network:** A pointwise 1x1 convolution outputs an update vector ($\Delta S$) of size $C$, applied residually as $S_{t+1} = S_t + \Delta S$.
* **State tensor dimensions:** An $H \times W \times 16$ tensor containing 4 visible channels (RGBA) and 12 hidden channels. The Alpha channel ($A$) acts as a live mask ($A > 0.1$).
* **Number of hidden channels used:** 12 hidden channels acting as latent memory for local message passing.
* **Training objective:** Mean Squared Error (L2 Loss) between predicted visible RGBA channels and the target image, trained via Backpropagation Through Time (BPTT) over a randomized number of steps (64-96).
