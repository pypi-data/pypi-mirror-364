pip install webdiver_v1

pip install requests beautifulsoup4 pandas

⚙️ Basic Functionality
set_task_uri(url: str)
Sets the URL that will be used in the web content reading and search task.

Example:

set_task_uri("https://example.com")

www_diver()
Reads the URL defined with set_task_uri() and stores the extracted information in the SQLite database.

Example:

www_diver()

sql_setup(db_name: str)
Creates and configures a .db file to keep records of searches performed by Web Diver.

Example:

sql_setup("webdiver_archive.db")

set_task(uri: str, hour: int, minute: int)
Schedules a new web crawling task for a specific time, setting the URL, hour, and minute for automatic execution.

Example:

set_task("https://example.com/news", 14, 30)

💡 Usage Examples

from webdiver import set_task_uri, www_diver, sql_setup, set_task

sql_setup("mydata.db")
set_task_uri("https://example.com")
www_diver()

# Task Scheduling
set_task("https://example.com", 12, 45)

🗃️ Database
The captured data is automatically stored in an SQLite database with information such as:

URL accessed

Simplified HTML content

Collection timestamp

👨‍💻 Developed by
#asytrick
Project available at: github.com/ssmool/webdiver