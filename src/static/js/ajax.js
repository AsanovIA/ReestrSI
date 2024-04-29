'use strict';
{
    window.addEventListener('load', function() {

        // Отправляем запрос
        function ajaxSend(url, params) {
            fetch(`${url}?${params}`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/x-www-urlencoded',
                },
            })
                .then(response => response.json())
                .then(json => render(json))
                .catch(error => console.error(error))
        };

        //Вывод ответа от сервера
        function render(data) {
            switch (data.element) {
                case 'employee':
                    render_employee(data.data);
                    break;
            }
        };

        //Изменение инфоррмации о выбранном employee
        const employee = document.querySelector('select[name=employee]');
        if (employee) {
            employee.addEventListener('change', () => {
                //Формирование запроса
                let url = '/valuechange/';
                let params = new URLSearchParams({
                    'element': 'employee',
                    'id': employee.value
                });
                ajaxSend(url, params);
            });
        };
        function render_employee(data) {
            //Вывод информации выбранном employee
            const new_division = document.querySelector('.id_division');
            new_division.innerHTML = data.division;
        };
    })
}
