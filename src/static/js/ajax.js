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
                case 'description_method':
                    render_description_method(data.data);
                    break;
            }
        };

        //Изменение информации о выбранном employee
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
            const new_email = document.querySelector('.id_email');
            new_division.innerHTML = data.division;
            new_email.innerHTML = data.email;
        };

        //Изменение информации о выбранном description_method
        const description_method = document.querySelector('select[name=description_method]');
        if (description_method) {
            description_method.addEventListener('change', () => {
                //Формирование запроса
                let url = '/valuechange/';
                let params = new URLSearchParams({
                    'element': 'description_method',
                    'id': description_method.value
                });
                ajaxSend(url, params);
            });
        };
        function render_description_method(data) {
            //Вывод информации выбранном description_method
            const new_description = document.querySelector('.id_description');
            const new_method = document.querySelector('.id_method');
            new_description.innerHTML = data.description;
            new_method.innerHTML = data.method;
        };
    })
}
