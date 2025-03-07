# Obscounter

A flexible, hotkey based counter for OBS Studio created in Python.


![prevew](counter.gif)

# Requirements

For Windows install [python3.6](https://www.python.org/downloads/release/python-368/) 64 or 32 bit depending on your OBS. Since 28 version OBS Studio supports most 3.x Python versions. The most recent version of this code was written using python3.12.

# Installation 

1. Download [source code](https://github.com/adamleif/Counter/archive/main.zip).
2. Unzip the file and place `hotkey_counter.py` in target directory. 

# Usage

1. In OBS, under Sources, click + to create a new Text GDI+ source. Format as desired. You may leave the text field blank.

![image](https://user-images.githubusercontent.com/2420577/214267000-44e091a0-eadb-43a2-ac68-d8763b172320.png)

2. In the OBS menu, click `Tools > Scripts`

![image](https://user-images.githubusercontent.com/2420577/214267186-562deac4-ee82-46df-8ebc-5278f9429f64.png)

3. Under the `Python Settings` tab, make sure your Python path is configured.

![image](https://user-images.githubusercontent.com/2420577/214267353-7155c08d-f9eb-4053-a17f-34ada6af86f5.png)

4. Under the `Scripts` tab, click the + sign to add `hotkey_counter.py` from your previously specified target directory.

![image](https://user-images.githubusercontent.com/2420577/214267447-cb5de6cc-5b98-44d6-bb5f-cccff76be836.png)

5. Close the scripts window, return to your OBS window, and configure OBS hotkey settings by clicking `File > Settings > Hotkeys`.

6. Configure the hotkeys.

![ui](https://i.imgur.com/UobLYdS.png)

![hotkeys](https://i.imgur.com/dEC2Y6M.png)

## How do I use more counters?

If you need additional counters, modify the `Number of Counters` field of the script in the OBS UI; then, refresh the script. Additional counters should appear in the sidebar, and additional hotkeys will be created for those counters.

# Contribute 

Contributions are welcome.
