# Whole Washington Volunteers Data Pipeline

## About the Project
Whole Washington volunteer coordinators need to keep track of new volunteers added via online or paper form.
This was previously done with a combination of manual work and Zapier.  This project is an attempt at a
low cost, self-serve alternative, to eventually be hosted on a secure server.

## Prerequisites
1. API key from [ActionNetwork API Page](https://admin.actionnetwork.org/groups/whole-washington/apis)
2. Access to this [ActionNetwork Report](https://admin.actionnetwork.org/reports/initial-download-for-python-code-janet-shen/manage)
3. PyCharm Installation (Community Edition is free)
4. Have Windows Task Scheduler or the equivalent for your operating system (requires admin access)
5. Have an invitation to the private Github repository: https://github.com/janetshen/whole_washington_volunteers

## Installation
1. If opening PyCharm for the first time, you will automatically be shown the New Project window.  If not, go to `File > Project from version control...`
2. Choose the option to log into Github and choose an existing repository.  For this example, we will choose to save our copy in `C:\Users\your_username\PycharmProjects\whole_washington_volunteers`
3. Navigate to the folder chosen in Step 2.  Create a copy of `.env_example`.  Rename the file `.env` and replace `abcdefg` with the API key.
   > [!CAUTION] Do not share or upload your copy of `.env` via the internet!  That includes Github.com! 
4. Close Pycharm and open Windows Task Scheduler
5. In the Actions menu of the upper right-hand corner, click `Create Task...`.  In the General tab, name the task and select the following options:
   - `Run whether user is logged on or not`
   - `Run with highest privileges`
6. In the Triggers tab, set the task to run once every day (if you left 'yesterday' entered in .env, I recommend setting it between 12:01AM and 01:00AM)
7. In the Actions tab, click New, and a New Action window will appear.  Set the following options:
   - Action: `Start a program`
   - Program/script: `C:\Users\your_username\PycharmProjects\whole_washington_volunteers\.venv\Scripts\python.exe`
   - Add arguments (optional): `C:\Users\your_username\PycharmProjects\whole_washington_volunteers\daily_updates.py`
   - Start in (optional): `C:\Users\your_username\PycharmProjects\whole_washington_volunteers`
8. In the Conditions tab, check the option `Wake the computer to run this task` and any other options that make sense for the machine
9. In the Settings tab, select the following options:
   - `Allow task to be run on demand`
   - `Run task as soon as possible after a scheduled start is missed`
   - `Stop the task if it runs longer than 2 hours`
   - `If the running task does not end when requested, force it to stop`
10. Click OK until prompted for Windows login password.  Enter password and click OK

## Roadmap
- [x] Sqlite file `volunteers.db`, updated daily, used to generate a different file per County
- [ ] Full-blown SQL mirror, which would normally cost $200 a month if purchased from ActionNetwork
- [ ] Automated reporting pulled from SQL mirror, to free up volunteer time

See the [open issues](https://github.com/janetshen/whole_washington_volunteers/issues) for a full list of proposed features (and known issues).

## Contributing
Contributions are what make the open source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

If you have a suggestion that would make this better, please fork the repo and create a pull request. You can also simply open an issue with the tag "enhancement".
Don't forget to give the project a star! Thanks again!

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## Top contributors:
<a href="https://github.com/janetshen/whole_washington_volunteer/sgraphs/contributors">
</a>

## License
Distributed under the project_license. See `LICENSE.txt` for more information.

## Contact
Janet Shen - janetshen_github@pm.me
Project Link: https://github.com/janetshen/whole_washington_volunteers

## Acknowledgments
* Thank you to Lindsey Sheehan for the opportunity to build this tool for the team!