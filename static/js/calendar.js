/**
 * Календарь задач с drag & drop функциональностью
 */

class TaskCalendar {
    constructor() {
        this.currentTask = null;
        this.isDragging = false;
        this.tasks = new Map();
        this.projectColors = new Map(); // Хранилище цветов для проектов
        this.init();
    }

    init() {
        console.log('Инициализация TaskCalendar...');

        // Проверяем, что jQuery UI загружен
        if (typeof $.fn.draggable === 'undefined' || typeof $.fn.resizable === 'undefined') {
            console.error('jQuery UI не загружен! Ожидаем загрузки...');
            setTimeout(() => this.init(), 1000);
            return;
        }

        // Добавляем задержку для полной загрузки DOM
        setTimeout(async () => {
            // Сначала загружаем задачи из localStorage (для совместимости)
            this.loadTasksFromStorage();

            // Пытаемся загрузить из БД, но не блокируем инициализацию при ошибке
            try {
                await this.loadTasksFromDatabase();
            } catch (error) {
                console.log('Загрузка из БД не удалась, используем localStorage:', error);
            }

            this.initializeDragDrop();
            this.initializeEventHandlers();
            console.log('TaskCalendar инициализирован');
        }, 500);
    }

    initializeDragDrop() {
        console.log('Инициализация drag & drop...');

        // Проверяем наличие элементов с разными селекторами
        const projectItems = $('.project-item');
        let calendarCells = $('.calendar-cell');
        const trashZone = $('#trash');

        // Если ячейки не найдены, пробуем альтернативные селекторы
        if (calendarCells.length === 0) {
            console.log('Ячейки не найдены по .calendar-cell, пробуем альтернативные селекторы...');
            calendarCells = $('td[data-staff-id]');
            console.log(`Найдено ячеек по td[data-staff-id]: ${calendarCells.length}`);
        }

        // Если все еще не найдены, пробуем найти по структуре таблицы
        if (calendarCells.length === 0) {
            console.log('Пробуем найти ячейки по структуре таблицы...');
            calendarCells = $('.table-responsive table tbody td:not(.staff-cell)');
            console.log(`Найдено ячеек по структуре таблицы: ${calendarCells.length}`);
        }

        console.log(`Найдено проектов: ${projectItems.length}`);
        console.log(`Найдено ячеек календаря: ${calendarCells.length}`);
        console.log(`Найдена корзина: ${trashZone.length}`);

        // Инициализация drag & drop для проектов
        projectItems.draggable({
            helper: function () {
                return $(this).clone().addClass('drag-helper');
            },
            revert: 'invalid',
            zIndex: 1000,
            start: (event, ui) => {
                console.log('Начало перетаскивания проекта:', $(event.target).data('project-name'));
                this.isDragging = true;
                $(event.target).addClass('dragging');
                $('.calendar-cell, td[data-staff-id]').addClass('drop-target');
            },
            stop: (event, ui) => {
                console.log('Окончание перетаскивания проекта');
                this.isDragging = false;
                $(event.target).removeClass('dragging');
                $('.calendar-cell, td[data-staff-id]').removeClass('drop-target');
            }
        });

        // Инициализация droppable для ячеек календаря
        if (calendarCells.length > 0) {
            calendarCells.each((index, cell) => {
                const $cell = $(cell);
                const staffId = $cell.data('staff-id');
                const day = $cell.data('day');

                if (staffId && day) {
                    console.log(`Инициализация ячейки ${staffId}-${day}`);

                    $cell.droppable({
                        accept: '.project-item, .task-item',
                        hoverClass: 'ui-droppable-hover',
                        tolerance: 'pointer',
                        over: (event, ui) => {
                            console.log(`Hover над ячейкой ${staffId}-${day}`);
                        },
                        drop: (event, ui) => {
                            const draggedElement = ui.draggable;
                            const targetCell = $(event.target).closest('td[data-staff-id]');
                            const targetStaffId = targetCell.data('staff-id');
                            const targetDay = targetCell.data('day');

                            console.log('Drop event:', {
                                targetStaffId,
                                targetDay,
                                element: draggedElement.attr('class'),
                                projectName: draggedElement.data('project-name'),
                                taskId: draggedElement.data('task-id')
                            });

                            if (draggedElement.hasClass('project-item')) {
                                // Перетаскивание проекта - создаем новую задачу
                                const projectId = draggedElement.data('project-id');
                                const projectName = draggedElement.data('project-name');
                                console.log(`Создание задачи из проекта: ${projectName} в ячейку ${targetStaffId}-${targetDay}`);
                                this.createTaskFromProject(projectId, projectName, targetStaffId, targetDay);
                            } else if (draggedElement.hasClass('task-item') || draggedElement.data('task-id')) {
                                // Перемещение существующей задачи
                                console.log(`Перемещение задачи в ячейку ${targetStaffId}-${targetDay}`);

                                // Находим исходную ячейку
                                const sourceCell = draggedElement.closest('td[data-staff-id]');
                                if (sourceCell.length > 0) {
                                    console.log('Исходная ячейка найдена:', sourceCell.data('staff-id'), sourceCell.data('day'));

                                    // Перемещаем задачу
                                    this.moveTask(draggedElement, targetStaffId, targetDay);

                                    // Автоматически выравниваем задачи в обеих ячейках
                                    this.autoArrangeTasksInCell(sourceCell);
                                    this.autoArrangeTasksInCell(targetCell);
                                } else {
                                    console.error('Исходная ячейка не найдена для задачи:', draggedElement.data('task-id'));
                                }
                            }
                        }
                    });
                } else {
                    console.log(`Ячейка ${index} не имеет data-staff-id или data-day:`, $cell.attr('class'));
                }
            });
        } else {
            console.error('Ячейки календаря не найдены! Проверьте HTML структуру.');
        }

        // Инициализация droppable для корзины
        trashZone.droppable({
            accept: '.task-item',
            hoverClass: 'ui-droppable-hover',
            tolerance: 'pointer',
            drop: (event, ui) => {
                const taskItem = ui.draggable;
                const taskId = taskItem.data('task-id');
                console.log(`Удаление задачи ${taskId} в корзину`);
                this.removeTask(taskId);
                taskItem.fadeOut(300, () => taskItem.remove());
            }
        });

        // Инициализация sortable для списков задач
        $('.task-list').sortable({
            connectWith: '.task-list',
            placeholder: 'task-placeholder',
            tolerance: 'pointer',
            // Убираем ограничение axis для свободного перемещения
            start: (event, ui) => {
                ui.item.addClass('dragging');
            },
            stop: (event, ui) => {
                ui.item.removeClass('dragging');
                this.updateTaskPosition(ui.item);
            }
        });

        // Также инициализируем sortable для ячеек календаря
        $('td[data-staff-id]').sortable({
            connectWith: 'td[data-staff-id]',
            placeholder: 'task-placeholder',
            tolerance: 'pointer',
            start: (event, ui) => {
                ui.item.addClass('dragging');
            },
            stop: (event, ui) => {
                ui.item.removeClass('dragging');
                this.updateTaskPosition(ui.item);
            }
        });

        // Устанавливаем position: relative для всех ячеек календаря
        $('td[data-staff-id]').css({
            'position': 'relative',
            'min-height': '200px', // Минимальная высота ячейки
            'border-right': '2px solid #dee2e6', // Разделитель между сотрудниками
            'padding-right': '10px', // Отступ справа для разделителя
            'border-left': '1px solid #dee2e6' // Разделитель слева
        });

        // Добавляем стили для заголовков столбцов сотрудников
        $('.staff-cell').css({
            'background-color': '#f8f9fa',
            'font-weight': 'bold',
            'border-bottom': '2px solid #dee2e6',
            'text-align': 'center',
            'border-right': '2px solid #dee2e6' // Разделитель справа
        });

        // Добавляем стили для таблицы
        $('.table-responsive table').css({
            'border-collapse': 'separate',
            'border-spacing': '0',
            'border': '2px solid #dee2e6'
        });

        // Добавляем специальную обработку для перетаскивания задач между ячейками
        $(document).on('drop', '.ui-droppable', (event, ui) => {
            const draggedElement = $(event.target);
            if (draggedElement.hasClass('task-item')) {
                console.log('Drop task detected:', draggedElement.data('task-id'));
            }
        });

        console.log('Drag & drop инициализирован');
    }

    // Функция для принудительной переинициализации
    reinitializeDragDrop() {
        console.log('Принудительная переинициализация drag & drop...');
        this.initializeDragDrop();
    }

    // Функция для проверки состояния элементов
    checkElements() {
        console.log('=== ПРОВЕРКА ЭЛЕМЕНТОВ ===');
        console.log('Проекты:', $('.project-item').length);
        console.log('Ячейки по .calendar-cell:', $('.calendar-cell').length);
        console.log('Ячейки по td[data-staff-id]:', $('td[data-staff-id]').length);
        console.log('Ячейки по структуре таблицы:', $('.table-responsive table tbody td:not(.staff-cell)').length);
        console.log('Корзина:', $('#trash').length);

        // Проверяем HTML структуру
        console.log('HTML структура таблицы:', $('.table-responsive table').html());

        return {
            projects: $('.project-item').length,
            calendarCells: $('.calendar-cell').length,
            dataCells: $('td[data-staff-id]').length,
            tableCells: $('.table-responsive table tbody td:not(.staff-cell)').length,
            trash: $('#trash').length
        };
    }

    initializeEventHandlers() {
        // Сохранение задачи
        $('#saveTask').off('click').on('click', () => {
            this.saveCurrentTask();
        });

        // Двойной клик по ячейке для быстрого добавления задачи
        $('.calendar-cell, td[data-staff-id]').off('dblclick').on('dblclick', (event) => {
            const staffId = $(event.currentTarget).data('staff-id');
            const day = $(event.currentTarget).data('day');
            this.showQuickTaskModal(staffId, day);
        });

        // Контекстное меню для задач
        $(document).off('contextmenu', '.task-item').on('contextmenu', '.task-item', (event) => {
            event.preventDefault();
            this.showTaskContextMenu(event);
        });
    }

    // Получение цвета для проекта (одинаковый для всех задач проекта)
    getProjectColor(projectId) {
        if (!this.projectColors.has(projectId)) {
            const color = this.getRandomColor();
            this.projectColors.set(projectId, color);
        }
        return this.projectColors.get(projectId);
    }

    createTaskFromProject(projectId, projectName, staffId, day) {
        // Проверяем, не создана ли уже задача для этого проекта в этой ячейке
        const existingTask = $(`[data-project-id="${projectId}"][data-staff-id="${staffId}"][data-day="${day}"]`);
        if (existingTask.length > 0) {
            console.log(`Задача для проекта ${projectName} уже существует в ячейке ${staffId}-${day}`);
            this.showAlert(`Задача для проекта "${projectName}" уже существует в этой ячейке`, 'warning');
            return existingTask.data('task-id');
        }

        // Проверяем, не создана ли уже задача для этого проекта у этого сотрудника
        const existingTaskForStaff = $(`[data-project-id="${projectId}"][data-staff-id="${staffId}"]`);
        if (existingTaskForStaff.length > 0) {
            console.log(`Задача для проекта ${projectName} уже существует у сотрудника ${staffId}`);
            this.showAlert(`Задача для проекта "${projectName}" уже существует у этого сотрудника`, 'warning');
            return existingTaskForStaff.data('task-id');
        }

        // Генерируем уникальный цвет для проекта (одинаковый для всех задач этого проекта)
        const projectColor = this.getProjectColor(projectId);

        // Создаем задачу напрямую без модального окна
        const taskId = this.createTask(staffId, day, projectName, 1, projectColor, null, projectId);

        // Показываем уведомление
        this.showAlert(`Задача "${projectName}" создана в ячейке ${staffId}-${day}`, 'success');

        return taskId;
    }

    showTaskModal(projectId, projectName, staffId, day) {
        $('#taskName').val(projectName);
        $('#taskDuration').val(1);
        $('#taskColor').val(this.getProjectColor(projectId));

        this.currentTask = {
            projectId: projectId,
            projectName: projectName,
            staffId: staffId,
            day: day
        };

        $('#taskModal').modal('show');
    }

    showQuickTaskModal(staffId, day) {
        $('#taskName').val('Новая задача');
        $('#taskDuration').val(1);
        $('#taskColor').val(this.getRandomColor());

        this.currentTask = {
            projectId: null,
            projectName: 'Новая задача',
            staffId: staffId,
            day: day
        };

        $('#taskModal').modal('show');
    }

    saveCurrentTask() {
        if (!this.currentTask) return;

        const taskName = $('#taskName').val().trim();
        const duration = parseInt($('#taskDuration').val());
        const color = $('#taskColor').val();

        if (!taskName || !duration) {
            this.showAlert('Пожалуйста, заполните все поля', 'warning');
            return;
        }

        this.createTask(this.currentTask.staffId, this.currentTask.day, taskName, duration, color);
        $('#taskModal').modal('hide');
        this.currentTask = null;
    }

    addTaskToCalendar(taskData) {
        console.log('Добавление задачи в календарь:', taskData);

        if (!taskData || !taskData.staffId || !taskData.day) {
            console.error('Неверные данные задачи:', taskData);
            return null;
        }

        const task = this.createTask(
            taskData.staffId,
            taskData.day,
            taskData.name,
            taskData.duration || 1,
            taskData.color || '#007bff',
            taskData.id,
            taskData.projectId
        );

        // Применяем правильное позиционирование после создания
        if (task) {
            this.fixTaskPositioning(taskData.staffId, taskData.day);
        }

        return task;
    }

    fixTaskPositioning(staffId, day) {
        // Исправляем позиционирование всех задач в ячейке
        const cell = $(`#cell_${staffId}_${day}`);
        if (cell.length > 0) {
            cell.find('.task-item').each(function (index) {
                const $task = $(this);
                const duration = $task.data('duration') || 1;

                // Задача должна начинаться с левого края
                $task.css({
                    'left': '0px !important',
                    'top': `${index * 32}px !important`, // Каждая следующая задача ниже
                    'width': `${duration * 80}px !important`,
                    'margin': '0 !important',
                    'margin-left': '0 !important',
                    'margin-right': '0 !important',
                    'margin-top': '0 !important',
                    'margin-bottom': '0 !important',
                    'z-index': duration > 1 ? '10' : '5'
                });

                // Принудительно убираем любые сдвиги
                setTimeout(() => {
                    $task.css({
                        'left': '0px !important',
                        'margin': '0 !important',
                        'margin-left': '0 !important',
                        'margin-right': '0 !important',
                        'margin-top': '0 !important',
                        'margin-bottom': '0 !important'
                    });
                }, 10);
            });
        }
    }

    fixAllTaskPositions() {
        console.log('Исправляем позиционирование всех задач...');

        // Проходим по всем ячейкам календаря
        $('.calendar-cell').each((index, cell) => {
            const $cell = $(cell);
            const staffId = $cell.data('staff-id');
            const day = $cell.data('day');

            if (staffId && day) {
                this.fixTaskPositioning(staffId, day);
            }
        });

        console.log('Позиционирование задач исправлено');
    }

    createTask(staffId, day, name, duration, color, taskId = null, projectId = null) {
        taskId = taskId || 'task_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);

        const taskHtml = `
            <li class="task-item new-task" 
                data-task-id="${taskId}" 
                data-duration="${duration}"
                data-staff-id="${staffId}"
                data-day="${day}"
                ${projectId ? `data-project-id="${projectId}"` : ''}
                style="background: ${color}; width: ${duration * 80}px; position: absolute; left: 0; top: 0; display: block; padding: 5px; margin: 0; border-radius: 3px; cursor: move; overflow: hidden; box-sizing: border-box; border: 1px solid rgba(0,0,0,0.1);">
                <span class="task-name" title="${name}" style="display: block; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; color: #333; font-size: 12px;">${name}</span>
                <button class="task-remove" onclick="taskCalendar.removeTask('${taskId}')" title="Удалить задачу" style="position: absolute; top: 2px; right: 5px; background: rgba(255,255,255,0.8); border: none; border-radius: 50%; width: 20px; height: 20px; cursor: pointer; font-weight: bold;">×</button>
            </li>
        `;

        // Ищем ячейку по разным способам
        let targetCell = $(`#cell_${staffId}_${day}`);
        if (targetCell.length === 0) {
            targetCell = $(`td[data-staff-id="${staffId}"][data-day="${day}"]`);
        }
        if (targetCell.length === 0) {
            targetCell = $(`td[data-staff-id="${staffId}"]`).filter((index, el) => {
                return $(el).data('day') === day;
            });
        }

        if (targetCell.length === 0) {
            console.error(`Ячейка для ${staffId}-${day} не найдена`);
            console.log('Доступные ячейки:', $('td[data-staff-id]').map((i, el) => {
                return `${$(el).data('staff-id')}-${$(el).data('day')}`;
            }).get());
            return null;
        }

        targetCell.append(taskHtml);
        console.log('HTML задачи добавлен в ячейку');

        // Применяем правильное позиционирование для задач с длительностью > 1 дня
        const taskElement = targetCell.find(`[data-task-id="${taskId}"]`);
        if (taskElement.length > 0) {
            // Задача должна начинаться с левого края ячейки
            taskElement.css({
                'left': '0px !important',
                'top': '0px !important',
                'width': `${duration * 80}px !important`,
                'margin': '0 !important',
                'margin-left': '0 !important',
                'margin-right': '0 !important',
                'margin-top': '0 !important',
                'margin-bottom': '0 !important',
                'padding-left': '5px !important',
                'padding-right': '5px !important'
            });

            // Если задача длится больше 1 дня, она должна выходить за границы ячейки
            if (duration > 1) {
                taskElement.css('z-index', '10');
            }

            // Принудительно убираем любые сдвиги
            setTimeout(() => {
                taskElement.css({
                    'left': '0px !important',
                    'margin': '0 !important',
                    'margin-left': '0 !important',
                    'margin-right': '0 !important',
                    'margin-top': '0 !important',
                    'margin-bottom': '0 !important'
                });
            }, 10);
        }

        // Сохраняем в localStorage и внутреннем хранилище
        const taskData = {
            id: taskId,
            staffId: staffId,
            day: day,
            name: name,
            duration: duration,
            color: color,
            projectId: projectId,
            created: new Date().toISOString()
        };

        this.saveTaskToStorage(taskId, taskData);
        this.tasks.set(taskId, taskData);

        // Ждем немного, чтобы DOM обновился
        setTimeout(() => {
            const taskElement = $(`[data-task-id="${taskId}"]`);
            if (taskElement.length === 0) {
                console.error(`Элемент задачи ${taskId} не найден после создания`);
                console.log('Попытка найти по другому селектору...');
                const allTasks = $('.task-item');
                console.log('Всего задач на странице:', allTasks.length);
                console.log('Последняя добавленная задача:', allTasks.last().attr('data-task-id'));

                // Пробуем найти по содержимому
                const taskByContent = $(`.task-item:contains("${name}")`);
                console.log('Задача найдена по содержимому:', taskByContent.length);

                if (taskByContent.length > 0) {
                    this.makeTaskDraggable(taskByContent);
                    this.makeTaskResizable(taskByContent);
                }
            } else {
                // Делаем задачу draggable
                this.makeTaskDraggable(taskElement);

                // Делаем задачу resizable
                this.makeTaskResizable(taskElement);

                // Проверяем, что задача стала draggable и resizable
                console.log('Задача draggable:', taskElement.hasClass('ui-draggable'));
                console.log('Задача resizable:', taskElement.hasClass('ui-resizable'));

                // Анимация появления
                taskElement.removeClass('new-task');

                // Автоматически выравниваем задачи в ячейке
                this.autoArrangeTasksInCell(targetCell);
            }
        }, 100);

        console.log(`Задача "${name}" создана в ячейке ${staffId}-${day}`);
        console.log('Ячейка найдена:', targetCell.length > 0);

        return taskId;
    }

    makeTaskDraggable(taskElement) {
        console.log('Делаем задачу draggable:', taskElement.attr('data-task-id'));

        // Проверяем, что jQuery UI draggable доступен
        if (typeof $.fn.draggable === 'undefined') {
            console.error('jQuery UI draggable не загружен!');
            return;
        }

        taskElement.draggable({
            revert: 'invalid',
            zIndex: 1000,
            // Убираем grid для свободного перемещения
            start: (event, ui) => {
                console.log('Начало перетаскивания задачи:', $(event.target).data('task-id'));
                $(event.target).addClass('dragging');
            },
            stop: (event, ui) => {
                console.log('Окончание перетаскивания задачи:', $(event.target).data('task-id'));
                $(event.target).removeClass('dragging');
            }
        });
    }

    makeTaskResizable(taskElement) {
        console.log('Делаем задачу resizable:', taskElement.attr('data-task-id'));

        // Проверяем, что jQuery UI resizable доступен
        if (typeof $.fn.resizable === 'undefined') {
            console.error('jQuery UI resizable не загружен!');
            return;
        }

        const cellWidth = 80; // Ширина ячейки календаря
        const totalDays = 31; // Общее количество дней в календаре

        taskElement.resizable({
            handles: 'e, w', // Возвращаем обе границы
            minWidth: 80, // Минимум 1 день
            maxWidth: totalDays * cellWidth, // Максимум 31 день
            grid: [cellWidth, 1], // Сетка по ширине ячейки (80px = 1 день)
            snap: true, // Привязка к сетке
            snapTolerance: 10, // Толерантность привязки
            // Убираем containment для свободного изменения размера
            // Добавляем специальную обработку для обеих границ
            // Исправляем проблему с левой границей
            resize: (event, ui) => {
                console.log('Resize event:', ui.size);
                console.log('Original size:', ui.originalSize);
                console.log('Element position:', ui.element.position());

                // Привязка к дням: одно движение = один день
                const newWidth = Math.round(ui.size.width / cellWidth) * cellWidth;
                const newDuration = Math.max(1, Math.round(newWidth / cellWidth));

                ui.element.data('duration', newDuration);
                ui.element.attr('data-duration', newDuration);

                // Обновляем ширину элемента строго по дням
                ui.element.css('width', newDuration * cellWidth + 'px');

                // Сбрасываем left позицию при изменении размера
                ui.element.css('left', '0');

                // Специальная обработка для левой границы
                if (ui.originalSize && ui.size.width !== ui.originalSize.width) {
                    const widthDiff = ui.size.width - ui.originalSize.width;
                    if (widthDiff > 0) {
                        // Увеличиваем размер вправо
                        console.log('Увеличение размера вправо на', widthDiff, 'px');
                    } else {
                        // Уменьшаем размер влево
                        console.log('Уменьшение размера влево на', Math.abs(widthDiff), 'px');
                    }
                }

                // Обновляем в хранилище
                const taskId = ui.element.data('task-id');
                if (this.tasks.has(taskId)) {
                    const taskData = this.tasks.get(taskId);
                    taskData.duration = newDuration;
                    this.saveTaskToStorage(taskId, taskData);
                }

                // Перевыравниваем задачи в ячейке после изменения размера
                const cell = ui.element.closest('td[data-staff-id]');
                if (cell.length > 0) {
                    this.autoArrangeTasksInCell(cell);
                }
            },
            stop: (event, ui) => {
                // Обновляем позицию задачи после изменения размера
                const taskId = ui.element.data('task-id');
                this.updateTaskAfterResize(taskId, ui.element);
            }
        });
    }

    updateTaskAfterResize(taskId, taskElement) {
        const taskData = this.tasks.get(taskId);
        if (taskData) {
            const newDuration = taskElement.data('duration');
            taskData.duration = newDuration;

            // Обновляем позицию элемента (left: 0 для начала дня)
            taskElement.css('left', '0');

            // Автоматически выравниваем задачи в ячейке
            const cell = taskElement.closest('td[data-staff-id]');
            if (cell.length > 0) {
                this.autoArrangeTasksInCell(cell);
            }

            this.saveTaskToStorage(taskId, taskData);
            this.tasks.set(taskId, taskData);

            this.showAlert(`Задача "${taskData.name}" изменена на ${newDuration} дней`, 'info');
        }
    }

    moveTask(taskElement, newStaffId, newDay) {
        const taskId = taskElement.data('task-id');
        const taskData = this.tasks.get(taskId);

        if (taskData) {
            // Находим целевую ячейку
            let targetCell = $(`td[data-staff-id="${newStaffId}"][data-day="${newDay}"]`);
            if (targetCell.length === 0) {
                targetCell = $(`td[data-staff-id="${newStaffId}"]`).filter((index, el) => {
                    return $(el).data('day') === newDay;
                });
            }

            if (targetCell.length > 0) {
                // Перемещаем элемент в новую ячейку
                targetCell.append(taskElement);

                // Обновляем данные задачи
                taskData.staffId = newStaffId;
                taskData.day = newDay;

                // Обновляем атрибуты элемента
                taskElement.attr('data-staff-id', newStaffId);
                taskElement.attr('data-day', newDay);

                // Обновляем позицию элемента (left: 0 для начала дня)
                taskElement.css('left', '0');

                // Сохраняем обновленные данные
                this.saveTaskToStorage(taskId, taskData);
                this.tasks.set(taskId, taskData);

                this.showAlert(`Задача "${taskData.name}" перемещена`, 'success');
            } else {
                this.showAlert(`Целевая ячейка ${newStaffId}-${newDay} не найдена`, 'error');
            }
        }
    }

    updateTaskPosition(taskItem) {
        const taskId = taskItem.data('task-id');
        const newCell = taskItem.closest('td[data-staff-id]');
        const newStaffId = newCell.data('staff-id');
        const newDay = newCell.data('day');

        console.log(`Обновление позиции задачи ${taskId} в ячейку ${newStaffId}-${newDay}`);

        if (this.tasks.has(taskId)) {
            const taskData = this.tasks.get(taskId);

            // Обновляем данные задачи
            taskData.staffId = newStaffId;
            taskData.day = newDay;

            // Обновляем атрибуты элемента
            taskItem.attr('data-staff-id', newStaffId);
            taskItem.attr('data-day', newDay);

            // Обновляем позицию элемента (left: 0 для начала дня)
            taskItem.css('left', '0');

            // Автоматически выравниваем задачи по высоте
            this.autoArrangeTasksInCell(newCell);

            // Сохраняем обновленные данные
            this.saveTaskToStorage(taskId, taskData);
            this.tasks.set(taskId, taskData);

            console.log(`Позиция задачи ${taskId} обновлена`);
        } else {
            console.error(`Задача ${taskId} не найдена в хранилище`);
        }
    }

    removeTask(taskId) {
        const taskElement = $(`[data-task-id="${taskId}"]`);
        const taskData = this.tasks.get(taskId);

        if (taskData) {
            this.showAlert(`Задача "${taskData.name}" удалена`, 'info');
        }

        taskElement.fadeOut(300, () => {
            taskElement.remove();
        });

        localStorage.removeItem('task_' + taskId);
        this.tasks.delete(taskId);
    }

    saveTaskToStorage(taskId, taskData) {
        localStorage.setItem('task_' + taskId, JSON.stringify(taskData));
    }

    loadTasksFromStorage() {
        for (let i = 0; i < localStorage.length; i++) {
            const key = localStorage.key(i);
            if (key && key.startsWith('task_')) {
                try {
                    const taskData = JSON.parse(localStorage.getItem(key));
                    if (taskData && taskData.id) {
                        this.createTask(
                            taskData.staffId,
                            taskData.day,
                            taskData.name,
                            taskData.duration,
                            taskData.color,
                            taskData.id,
                            taskData.projectId
                        );
                    }
                } catch (e) {
                    console.warn('Ошибка загрузки задачи:', key, e);
                    localStorage.removeItem(key);
                }
            }
        }
    }

    // Загрузка задач из базы данных
    async loadTasksFromDatabase() {
        try {
            console.log('Загрузка задач из базы данных...');

            // Проверяем, существует ли API endpoint
            const response = await fetch('/api/tasks/', {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                }
            });

            if (response.ok) {
                const tasks = await response.json();
                console.log(`Загружено ${tasks.length} задач из БД`);

                // Очищаем текущие задачи
                this.clearAllTasks();

                // Создаем задачи из полученных данных
                tasks.forEach(taskData => {
                    this.createTask(
                        taskData.staff_id || taskData.staffId,
                        taskData.day,
                        taskData.name,
                        taskData.duration,
                        taskData.color,
                        taskData.id,
                        taskData.project_id || taskData.projectId
                    );
                });

                this.showAlert(`Загружено ${tasks.length} задач из базы данных`, 'success');
            } else if (response.status === 404) {
                console.log('API endpoint не найден, пропускаем загрузку из БД');
                this.showAlert('API для загрузки не настроен, используем localStorage', 'info');
                return; // Не показываем ошибку, если endpoint просто не существует
            } else {
                console.warn('Ошибка загрузки из БД:', response.status);
                this.showAlert('Ошибка загрузки задач из базы данных', 'warning');
            }
        } catch (error) {
            if (error.name === 'TypeError' && error.message.includes('fetch')) {
                console.log('Fetch API не поддерживается, пропускаем загрузку из БД');
                this.showAlert('API для загрузки не поддерживается, используем localStorage', 'info');
                return; // Не показываем ошибку для старых браузеров
            }
            console.error('Ошибка загрузки из БД:', error);
            this.showAlert('Ошибка загрузки задач из базы данных', 'danger');
        }
    }

    // Сохранение задач в базу данных
    async autoSaveToDatabase() {
        try {
            console.log('Сохранение задач в базу данных...');

            const tasksArray = Array.from(this.tasks.values());

            // Сначала сохраняем в localStorage как резервную копию
            tasksArray.forEach(taskData => {
                this.saveTaskToStorage(taskData.id, taskData);
            });

            const response = await fetch('/api/tasks/save/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                },
                body: JSON.stringify({ tasks: tasksArray })
            });

            if (response.ok) {
                const result = await response.json();
                console.log('Задачи сохранены в БД:', result);
                this.showAlert('Задачи успешно сохранены в базу данных', 'success');
            } else if (response.status === 404) {
                console.log('API endpoint не найден, пропускаем сохранение в БД');
                this.showAlert('API для сохранения не настроен, используем localStorage', 'info');
            } else {
                console.warn('Ошибка сохранения в БД:', response.status);
                this.showAlert('Ошибка сохранения задач в базу данных', 'warning');
            }
        } catch (error) {
            if (error.name === 'TypeError' && error.message.includes('fetch')) {
                console.log('Fetch API не поддерживается, пропускаем сохранение в БД');
                this.showAlert('API для сохранения не поддерживается, используем localStorage', 'info');
                return;
            }
            console.error('Ошибка сохранения в БД:', error);
            this.showAlert('Ошибка сохранения задач в базу данных', 'danger');
        }
    }

    // Автоматическое выравнивание задач по высоте в ячейке
    autoArrangeTasksInCell(cell) {
        const tasks = cell.find('.task-item');
        const taskHeight = 32; // Высота одной задачи
        const spacing = 2; // Отступ между задачами
        const maxTasksPerColumn = 5; // Максимум задач в одном столбце

        console.log(`Выравнивание ${tasks.length} задач в ячейке`);

        // Сортируем задачи по начальному дню для правильного выравнивания
        const sortedTasks = tasks.toArray().sort((a, b) => {
            const dayA = parseInt($(a).data('day')) || 0;
            const dayB = parseInt($(b).data('day')) || 0;
            return dayA - dayB;
        });

        sortedTasks.forEach((task, index) => {
            const $task = $(task);

            // Простое выравнивание по высоте - каждая задача ниже предыдущей
            const topPosition = index * (taskHeight + spacing);

            $task.css({
                'position': 'absolute',
                'top': `${topPosition}px`,
                'left': '0', // Всегда начинаем с левого края
                'z-index': index + 1
            });

            console.log(`Задача ${index}: top=${topPosition}px`);
        });

        // Увеличиваем высоту ячейки, если нужно
        if (sortedTasks.length > 0) {
            const lastTask = sortedTasks[sortedTasks.length - 1];
            const lastTaskBottom = $(lastTask).position().top + taskHeight + spacing;
            const currentCellHeight = cell.height();

            if (lastTaskBottom > currentCellHeight) {
                cell.css('min-height', lastTaskBottom + 'px');
                console.log(`Высота ячейки увеличена до ${lastTaskBottom}px`);
            }
        }
    }

    // Выравнивание всех задач во всех ячейках
    autoArrangeAllTasks() {
        console.log('Выравнивание всех задач...');

        // Находим все ячейки с задачами
        const cells = $('td[data-staff-id]');

        cells.each((index, cell) => {
            const $cell = $(cell);
            if ($cell.find('.task-item').length > 0) {
                this.autoArrangeTasksInCell($cell);
            }
        });

        this.showAlert('Все задачи выровнены', 'success');
    }

    // Принудительное выравнивание задач
    forceArrangeTasks() {
        console.log('Принудительное выравнивание задач...');

        // Находим все ячейки с задачами
        const cells = $('td[data-staff-id]');
        console.log(`Найдено ${cells.length} ячеек`);

        // Выравниваем задачи в каждой ячейке
        cells.each((index, cell) => {
            const $cell = $(cell);
            if ($cell.find('.task-item').length > 0) {
                this.autoArrangeTasksInCell($cell);
            }
        });

        this.showAlert('Задачи принудительно выровнены', 'success');
    }

    // Тестирование создания задачи
    testCreateTask() {
        console.log('Тестирование создания задачи...');

        // Находим первую доступную ячейку
        const firstCell = $('td[data-staff-id]').first();
        if (firstCell.length === 0) {
            this.showAlert('Ячейки не найдены!', 'danger');
            return;
        }

        const staffId = firstCell.data('staff-id');
        const day = firstCell.data('day');

        console.log(`Создаем тестовую задачу в ячейке ${staffId}-${day}`);

        const taskId = this.createTask(staffId, day, 'Тестовая задача', 2, '#ff0000');

        if (taskId) {
            this.showAlert('Тестовая задача создана успешно!', 'success');
        } else {
            this.showAlert('Ошибка создания тестовой задачи!', 'danger');
        }
    }

    // Тестирование перемещения задачи
    testMoveTask() {
        console.log('Тестирование перемещения задачи...');

        // Находим первую задачу
        const firstTask = $('.task-item').first();
        if (firstTask.length === 0) {
            this.showAlert('Задачи не найдены! Сначала создайте задачу.', 'warning');
            return;
        }

        // Находим другую ячейку для перемещения
        const currentCell = firstTask.closest('td[data-staff-id]');
        const otherCell = $('td[data-staff-id]').not(currentCell).first();

        if (otherCell.length === 0) {
            this.showAlert('Другие ячейки не найдены!', 'warning');
            return;
        }

        const newStaffId = otherCell.data('staff-id');
        const newDay = otherCell.data('day');

        console.log(`Перемещаем задачу в ячейку ${newStaffId}-${newDay}`);

        this.moveTask(firstTask, newStaffId, newDay);
        this.showAlert('Задача перемещена!', 'success');
    }

    // Тестирование resize
    testResize() {
        console.log('Тестирование resize...');

        // Находим первую задачу
        const firstTask = $('.task-item').first();
        if (firstTask.length === 0) {
            this.showAlert('Задачи не найдены! Сначала создайте задачу.', 'warning');
            return;
        }

        console.log('Текущая ширина задачи:', firstTask.width());
        console.log('Текущая длительность:', firstTask.data('duration'));

        // Пытаемся изменить размер
        const newWidth = firstTask.width() + 80; // Увеличиваем на 1 день
        firstTask.css('width', newWidth + 'px');

        // Обновляем данные
        const newDuration = Math.round(newWidth / 80);
        firstTask.data('duration', newDuration);
        firstTask.attr('data-duration', newDuration);

        console.log('Новая ширина:', newWidth);
        console.log('Новая длительность:', newDuration);

        this.showAlert(`Размер задачи изменен на ${newDuration} дней`, 'success');
    }

    // Тестирование левой границы resize
    testLeftResize() {
        console.log('Тестирование левой границы resize...');

        // Находим первую задачу
        const firstTask = $('.task-item').first();
        if (firstTask.length === 0) {
            this.showAlert('Задачи не найдены! Сначала создайте задачу.', 'warning');
            return;
        }

        console.log('Текущая ширина задачи:', firstTask.width());
        console.log('Текущая длительность:', firstTask.data('duration'));

        // Пытаемся уменьшить размер с левой стороны
        const currentWidth = firstTask.width();
        const newWidth = Math.max(80, currentWidth - 80); // Уменьшаем на 1 день, но не меньше 80px

        firstTask.css('width', newWidth + 'px');

        // Обновляем данные
        const newDuration = Math.round(newWidth / 80);
        firstTask.data('duration', newDuration);
        firstTask.attr('data-duration', newDuration);

        console.log('Новая ширина:', newWidth);
        console.log('Новая длительность:', newDuration);

        this.showAlert(`Размер задачи изменен на ${newDuration} дней (левая граница)`, 'success');
    }

    // Получение CSRF токена
    getCSRFToken() {
        // Пробуем разные способы получения CSRF токена
        let token = document.querySelector('[name=csrfmiddlewaretoken]');
        if (token) return token.value;

        token = document.querySelector('meta[name=csrf-token]');
        if (token) return token.getAttribute('content');

        token = document.querySelector('input[name=csrfmiddlewaretoken]');
        if (token) return token.value;

        // Если токен не найден, возвращаем пустую строку
        console.warn('CSRF токен не найден');
        return '';
    }

    getRandomColor() {
        const colors = [
            '#007bff', '#28a745', '#dc3545', '#ffc107',
            '#17a2b8', '#6f42c1', '#fd7e14', '#20c997',
            '#6610f2', '#e83e8c'
        ];
        return colors[Math.floor(Math.random() * colors.length)];
    }

    showAlert(message, type = 'info') {
        const alertHtml = `
            <div class="alert alert-${type} alert-dismissible fade show position-fixed" 
                 style="top: 20px; right: 20px; z-index: 9999; min-width: 300px;">
                ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            </div>
        `;

        $('body').append(alertHtml);

        // Автоматическое удаление через 3 секунды
        setTimeout(() => {
            $('.alert').fadeOut(300, function () {
                $(this).remove();
            });
        }, 3000);
    }

    showTaskContextMenu(event) {
        // Пока простая реализация - показываем alert с информацией о задаче
        const taskElement = $(event.currentTarget);
        const taskId = taskElement.data('task-id');
        const taskData = this.tasks.get(taskId);

        if (taskData) {
            const info = `
Задача: ${taskData.name}
Длительность: ${taskData.duration} дней
Сотрудник: ${taskData.staffId}
День: ${taskData.day}
Создана: ${new Date(taskData.created).toLocaleString()}
            `;
            alert(info);
        }
    }

    // Экспорт задач
    exportTasks() {
        const tasksArray = Array.from(this.tasks.values());
        const dataStr = JSON.stringify(tasksArray, null, 2);
        const dataBlob = new Blob([dataStr], { type: 'application/json' });

        const link = document.createElement('a');
        link.href = URL.createObjectURL(dataBlob);
        link.download = 'tasks_export.json';
        link.click();
    }

    // Импорт задач
    importTasks(file) {
        const reader = new FileReader();
        reader.onload = (e) => {
            try {
                const tasksData = JSON.parse(e.target.result);

                // Очищаем текущие задачи
                this.clearAllTasks();

                // Загружаем новые задачи
                tasksData.forEach(taskData => {
                    this.createTask(
                        taskData.staffId,
                        taskData.day,
                        taskData.name,
                        taskData.duration,
                        taskData.color,
                        taskData.id,
                        taskData.projectId
                    );
                });

                this.showAlert('Задачи успешно импортированы', 'success');
            } catch (error) {
                this.showAlert('Ошибка импорта задач', 'danger');
                console.error('Ошибка импорта:', error);
            }
        };
        reader.readAsText(file);
    }

    getAllTasks() {
        console.log('Получение всех задач...');
        const tasks = [];

        $('.task-item').each(function () {
            const $task = $(this);
            const taskData = {
                id: $task.data('task-id'),
                name: $task.text().trim(),
                staffId: $task.data('staff-id'),
                day: $task.data('day'),
                duration: $task.data('duration'),
                color: $task.css('background-color'),
                projectId: $task.data('project-id')
            };
            tasks.push(taskData);
        });

        console.log('Найдено задач:', tasks.length);
        return tasks;
    }

    clearAllTasks() {
        $('.task-item').remove();
        this.tasks.clear();

        // Очищаем localStorage
        for (let i = localStorage.length - 1; i >= 0; i--) {
            const key = localStorage.key(i);
            if (key && key.startsWith('task_')) {
                localStorage.removeItem(key);
            }
        }
    }

    // Получение статистики
    getStatistics() {
        const stats = {
            totalTasks: this.tasks.size,
            tasksByStaff: new Map(),
            tasksByDay: new Map(),
            averageDuration: 0
        };

        let totalDuration = 0;

        this.tasks.forEach(task => {
            // По сотрудникам
            if (!stats.tasksByStaff.has(task.staffId)) {
                stats.tasksByStaff.set(task.staffId, 0);
            }
            stats.tasksByStaff.set(task.staffId, stats.tasksByStaff.get(task.staffId) + 1);

            // По дням
            if (!stats.tasksByDay.has(task.day)) {
                stats.tasksByDay.set(task.day, 0);
            }
            stats.tasksByDay.set(task.day, stats.tasksByDay.get(task.day) + 1);

            totalDuration += task.duration;
        });

        stats.averageDuration = stats.totalTasks > 0 ? totalDuration / stats.totalTasks : 0;

        return stats;
    }
}

// Глобальная переменная для доступа к календарю
let taskCalendar;

// Инициализация при загрузке страницы
$(document).ready(function () {
    taskCalendar = new TaskCalendar();

    // Добавляем кнопки управления только один раз
    if ($('.calendar-controls').length === 0) {
        addControlButtons();
    }
});

function addControlButtons() {
    const controlsHtml = `
        <div class="calendar-controls mb-3">
            <div class="btn-group" role="group">
                <button type="button" class="btn btn-primary btn-sm" onclick="taskCalendar.showQuickTaskModal(1, 1)">
                    <i class="fas fa-plus"></i> Добавить задачу
                </button>
                <button type="button" class="btn btn-info btn-sm" onclick="showStatistics()">
                    <i class="fas fa-chart-bar"></i> Статистика
                </button>
                <button type="button" class="btn btn-success btn-sm" onclick="taskCalendar.exportTasks()">
                    <i class="fas fa-download"></i> Экспорт
                </button>
                <button type="button" class="btn btn-warning btn-sm" onclick="$('#importFile').click()">
                    <i class="fas fa-upload"></i> Импорт
                </button>
                <button type="button" class="btn btn-danger btn-sm" onclick="clearAllTasks()">
                    <i class="fas fa-trash"></i> Очистить все
                </button>
                <button type="button" class="btn btn-secondary btn-sm" onclick="taskCalendar.checkElements()">
                    <i class="fas fa-search"></i> Проверить элементы
                </button>
                <button type="button" class="btn btn-warning btn-sm" onclick="taskCalendar.reinitializeDragDrop()">
                    <i class="fas fa-redo"></i> Переинициализировать
                </button>
            </div>
            <div class="btn-group mt-2" role="group">
                <button type="button" class="btn btn-primary btn-sm" onclick="taskCalendar.loadTasksFromDatabase()">
                    <i class="fas fa-database"></i> Загрузить из БД
                </button>
                <button type="button" class="btn btn-success btn-sm" onclick="taskCalendar.autoSaveToDatabase()">
                    <i class="fas fa-save"></i> Сохранить в БД
                </button>
                <button type="button" class="btn btn-info btn-sm" onclick="taskCalendar.autoArrangeAllTasks()">
                    <i class="fas fa-align-justify"></i> Выровнять все
                </button>
                <button type="button" class="btn btn-warning btn-sm" onclick="taskCalendar.testCreateTask()">
                    <i class="fas fa-plus"></i> Тест задачи
                </button>
                <button type="button" class="btn btn-info btn-sm" onclick="taskCalendar.testMoveTask()">
                    <i class="fas fa-arrows-alt"></i> Тест перемещения
                </button>
                <button type="button" class="btn btn-success btn-sm" onclick="taskCalendar.forceArrangeTasks()">
                    <i class="fas fa-align-justify"></i> Принудительно выровнять
                </button>
                <button type="button" class="btn btn-warning btn-sm" onclick="taskCalendar.testResize()">
                    <i class="fas fa-expand-arrows-alt"></i> Тест resize
                </button>
                <button type="button" class="btn btn-danger btn-sm" onclick="taskCalendar.testLeftResize()">
                    <i class="fas fa-compress-arrows-alt"></i> Тест левой границы
                </button>
            </div>
        </div>
        <input type="file" id="importFile" style="display: none;" accept=".json" onchange="handleImport(event)">
    `;

    $('.card-body .table-responsive').before(controlsHtml);
}

function showStatistics() {
    if (typeof taskCalendar === 'undefined') {
        alert('Календарь не инициализирован');
        return;
    }

    const stats = taskCalendar.getStatistics();

    let statsHtml = `
        <h6>Статистика задач:</h6>
        <p>Всего задач: ${stats.totalTasks}</p>
        <p>Средняя длительность: ${stats.averageDuration.toFixed(1)} дней</p>
    `;

    if (stats.tasksByStaff.size > 0) {
        statsHtml += '<h6>По сотрудникам:</h6><ul>';
        stats.tasksByStaff.forEach((count, staffId) => {
            statsHtml += `<li>Сотрудник ${staffId}: ${count} задач</li>`;
        });
        statsHtml += '</ul>';
    }

    alert(statsHtml.replace(/<[^>]*>/g, '\n'));
}

function handleImport(event) {
    const file = event.target.files[0];
    if (file) {
        taskCalendar.importTasks(file);
    }
}

function clearAllTasks() {
    if (typeof taskCalendar === 'undefined') {
        alert('Календарь не инициализирован');
        return;
    }

    if (confirm('Вы уверены, что хотите удалить все задачи?')) {
        taskCalendar.clearAllTasks();
        taskCalendar.showAlert('Все задачи удалены', 'info');
    }
}
