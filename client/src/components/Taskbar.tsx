import React, { useState } from 'react';

// Define a Task interface for the task objects
interface Task {
  id: number;
  name: string;
}

const Taskbar: React.FC = () => {
  // State to keep track of the active task
  const [activeTask, setActiveTask] = useState<Task | null>(null);

  // Function to handle task click
  const handleTaskClick = (task: Task) => {
    setActiveTask(task);
    // Perform any other actions related to task click
  };

  // Dummy list of tasks, you can replace this with your actual data
  const tasks: Task[] = [
    { id: 1, name: 'Task 1' },
    { id: 2, name: 'Task 2' },
    { id: 3, name: 'Task 3' },
  ];

  return (
    <div className="taskbar">
      <ul className="task-list">
        {tasks.map((task) => (
          <li
            key={task.id}
            className={activeTask === task ? 'active-task' : ''}
            onClick={() => handleTaskClick(task)}
          >
            {task.name}
          </li>
        ))}
      </ul>
    </div>
  );
};

export default Taskbar;