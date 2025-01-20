### 1. Provision of SIM7600 (LTE) modules (Qty: 2) + Antennas (Qty: 2 sets) and installation manual

### 2. You have confirmed that you can handle the custom production steps
Ans: YES

### 3. Clone and restore master system image from one unit to many and provision every unit using script we provide before shipping
Ans: YES

### 4. Please provide manual instruction to create and restore a system image with in-built tool
Ans: please refer to https://github.com/artilatw/docs/blob/main/matrix752U/backup_n_restore.md

### 5. Check if possible to automatically retrieve unique per device UUID and print it on the label
Ans: Each Matrix-752U device comes with multiple unique identifiers:

<<<<<<< HEAD
1. Serial Number: A unique serial number is assigned to each device during manufacturing
2. MAC Addresses: Each device has two unique MAC addresses (one for each network interface)

The serial number and MAC addresses are already printed on the product label (at the backside of the device).

You can provide your own MAC address for the device.
=======
- Serial Number: A unique serial number is assigned to each device during manufacturing
- MAC Addresses: Each device has two unique MAC addresses (one for each network interface)
>>>>>>> 7c7321d (update)

The serial number and MAC addresses can be printed on the physical label. You can provide your own MAC address for the device.

### 6. Hitachi Energy custom labels with small QR code pointing to online hosted operating/installation manual
Ans: YES
<<<<<<< HEAD

&nbsp;&nbsp;&nbsp;
=======
>>>>>>> 7c7321d (update)

### 7. Can you describe the Secure Boot process , and what is the timeline for its implementation ?
Ans: Our Linux platform uses open-source code to build the system image. We will continue upgrading the kernel to stay as close to the latest version as possible. Our goal is to maintain our Linux platform as open and standard as possible.

<<<<<<< HEAD
So the concerning point of the security is not related to the Linux kernel, but related to the security of the user application.

Most of our customers bind their applications to the MAC address of the device. Our customers usually prepare their MAC addresses to us, and once the MAC address is programmed into the device, it cannot be changed. Users applications need to check the MAC address to make sure the application is running on the correct device.

Please let us know if you accept the above security measures.

### 8. Possibility for larger eMMC storage (e.g. 32GB), can you please indicate the cost increase for the 32GB eMMC option ? 
Ans: It is OK to ship with 32GB eMMC. The cost increase is USD 3 per unit.
=======
The main security concern is not about the Linux kernel itself, but rather about protecting the user applications. Most of our customers implement MAC address binding as their security measure, which is described below:

- Customers provide their own MAC addresses
- MAC addresses are permanently programmed into devices during manufacturing
- Applications verify device MAC addresses before running
- Ensures applications only run on authorized devices

Please let us know if you accept the above security measures. We can also discuss additional security requirements if needed, such as: OP-TEE, TEE, etc.

### 8. Possibility for larger eMMC storage (e.g. 32GB), can you please indicate the cost increase for the 32GB eMMC option ? 
Ans: It is possible. Actually we have a plan to upgrade the eMMC storage to 32GB in the future.
>>>>>>> 7c7321d (update)

### 9. Can you please indicate the potential cost for the extra manufacturing steps (Custom labels, System image loading, etc). We would like to evaluate the final full cost per unit.
Ans: We usually charge an additional USD 5~10 per unit for the extra manufacturing steps, depending on the complexity of the steps and the number of units.

