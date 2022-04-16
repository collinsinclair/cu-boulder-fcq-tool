from search_interpreter import Search

while True:
    user_search = input("Enter search: ")
    if user_search == "exit":
        break
    search = Search(user_search)
    search.parse_all()
    print("Subject: {}".format(search.subject))
    print("Course: {}".format(search.course))
    print("College: {}".format(search.college))
    print("Department: {}".format(search.department))
    print("Instructor: {}".format(search.instructor_name))
    print("")
