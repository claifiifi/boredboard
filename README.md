# BoredBoard
BoredBoard is a program built using Flask that helps you manage tasks and deadlines. It provides a web-based interface to create, update, and delete tasks, and organizes them based on their due dates.

## Features

- Create tasks with titles, descriptions, and due dates.
- View tasks organized by due dates, including today, tomorrow, this week, upcoming, and overdue tasks.
- Update task details such as title, description, and due date.
- Delete tasks when they are no longer needed.
- Multiple boards to manage different sets of tasks.
- Password protection for each board to ensure privacy and access control.

## Prerequisites

Before running the Task Manager, make sure you have the following:

- Python 3.x installed on your system.
- Flask and psycopg2 Python libraries installed. You can install them using pip:

```shell
pip install Flask psycopg2
```

- PostgreSQL database with the required schema set up. Refer to the `schema.sql` file for the database schema.

## Installation

1. Clone the repository or download the source code.

```shell
git clone https://github.com/yourusername/task-manager.git
```

2. Navigate to the project directory.

```shell
cd task-manager
```

3. Install the required dependencies.

```shell
pip install -r requirements.txt
```

4. Configure the database connection settings in the `create_app()` function of `app.py`.

```python
app.config['postgreSQL_pool'] = psycopg2.pool.SimpleConnectionPool(
    1, 20, user="yourusername",
    password="yourpassword",
    host="yourdatabasehost",
    port="yourdatabaseport",
    database="yourdatabasename"
)
```

5. Run the application.

```shell
python app.py
```

6. Open your web browser and navigate to `http://localhost:5000` to access the Task Manager.

## Usage

1. Home Page

- If a board cookie is set, you will be redirected to the respective board's tasks page.
- Otherwise, you can create a new board or enter an existing board number and password.

2. Board Page

- After entering a valid board number and password, you will be directed to the board's tasks page.
- The tasks are organized based on their due dates, and you can click on a task to view its details.
- You can create new tasks, update existing tasks, or delete tasks from this page.

## License

The Task Manager is open-source software licensed under the [MIT License](https://opensource.org/licenses/MIT).

## Acknowledgments

The Task Manager is built using the Flask web framework and uses PostgreSQL as the backend database. It relies on various open-source libraries and components, including:

- Flask: [https://flask.palletsprojects.com/](https://flask.palletsprojects.com/)
- psycopg2: [https://www.psycopg.org/](https://www.psycopg.org/)
- Bootstrap: [https://getbootstrap.com/](https://getbootstrap.com/)

## Contributing

Contributions to the Task Manager are welcome! If you have any ideas, improvements, or bug fixes, please feel free to submit a pull request or open an issue on the GitHub repository.

## Contact

For any questions or inquiries, please contact [your-email@example.com](mailto:your-email@example.com).

---

Feel free to customize this README.md file as per your specific requirements and add any additional sections or information that you think would be relevant.
