// region  đặt lịch
const form = document.querySelector("form")
const resultContainer = document.getElementById("resultContainer");
const newPatientContainer = document.getElementById("newPatientContainer");

async function searchPatient() {
    const phone = document.getElementById("phone").value;
    try {
        const res = await fetch(`/api/datlich/${phone}`);
        // Kiểm tra xem phản hồi có thành công không
        if (!res.ok) {
            throw new Error("Có lỗi xảy ra khi tìm kiếm bệnh nhân.");
        }
        const patient = await res.json();
        // Kiểm tra nếu có lỗi trong dữ liệu trả về
        if (patient.error) {
            alert(patient.error); // Hiển thị thông báo lỗi từ server
            resultContainer.classList.add("hidden");
            return;
        }
        // Lưu ID bệnh nhân vào sessionStorage
        sessionStorage.setItem("patient_id", patient.id);
        // Hiển thị thông tin bệnh nhân
        document.getElementById("resultName").innerText = patient["name"];
        document.getElementById("resultBirthYear").innerText = patient["birthday"];
        document.getElementById("resultGender").innerText = patient["gender"];
        document.getElementById("resultPhone").innerText = patient["sdt"];
        resultContainer.classList.remove("hidden");
    } catch (error) {
        // Xử lý lỗi
        console.error("Lỗi:", error);
        alert("Không tìm thấy bệnh nhân. Vui lòng kiểm tra lại số điện thoại.");
        resultContainer.classList.add("hidden");
    }
}

function usePatientInfo() {
    // Lấy thông tin từ kết quả tìm kiếm
    const name = document.getElementById("resultName").innerText;
    const phone = document.getElementById("resultPhone").innerText;
    const birthYear = document.getElementById("resultBirthYear").innerText;
    const gender = document.getElementById('resultGender').innerText;

    // Điền dữ liệu vào các ô nhập liệu
    document.getElementById("Ten").value = name;
    document.getElementById("phone1").value = phone;
    document.getElementById("ngaySinh").value = birthYear;
    // Đặt giới tính vào radio button
    if (gender === "nam") {
        document.getElementById("nam").checked = true;
    } else if (gender === "nữ") {
        document.getElementById("nu").checked = true;
    }

    // Chuyển các ô nhập liệu thành readonly
    document.getElementById("Ten").readOnly = true;
    document.getElementById("phone1").readOnly = true;
    document.getElementById("ngaySinh").readOnly = true;
    // Khóa radio button (không cho thay đổi giới tính)
    document.getElementById("nam").disabled = true;
    document.getElementById("nu").disabled = true;
    document.getElementById("thembn").disabled = true
    //Hiện đặt lịch
    const isDatLich = document.querySelectorAll(".isDatLich")
    isDatLich.forEach(e => e.classList.remove("hidden"))
    // Hiển thị form mới (nếu cần)
    newPatientContainer.classList.remove("hidden");
}


function resetSearch() {
    sessionStorage.removeItem("patient_id")
    document.getElementById("nam").disabled = false;
    document.getElementById("nu").disabled = false;
    document.getElementById("Ten").readOnly = false;
    document.getElementById("phone1").readOnly = false;
    document.getElementById("ngaySinh").readOnly = false;
    document.getElementById("thembn").disabled = false
    const isDatLich = document.querySelectorAll(".isDatLich")
    document.getElementById('resultContainer').classList.add('hidden')
    isDatLich.forEach(e => e.classList.add("hidden"))
    form.reset();
}

function resetForm() {
    resetSearch();
}

function addPatient() {
    const patientData = {
        name: document.getElementById('Ten').value,
        phone: document.getElementById('phone1').value,
        birthYear: document.getElementById('ngaySinh').value,
        gender: document.querySelector('input[name="gioiTinh"]:checked').value,
    };

    fetch('/api/add_patient', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(patientData)
    })
        .then(response => {
            return response.json();
        })
        .then(data => {
            if (data.id) {
                sessionStorage.setItem("patient_id", data.id)
                document.getElementById("Ten").readOnly = true;
                document.getElementById("phone1").readOnly = true;
                document.getElementById("ngaySinh").readOnly = true;
                // Khóa radio button (không cho thay đổi giới tính)
                document.getElementById("nam").disabled = true;
                document.getElementById("nu").disabled = true;
            }
            if (data.message)
                alert(data.message);
            else alert(data.error)
        })
        .catch(error => {
            console.error('Lỗi khi fetch:', error);
            alert('Có lỗi xảy ra khi thêm bệnh nhân.');
        });
    const isDatLich = document.querySelectorAll(".isDatLich")
    isDatLich.forEach(e => e.classList.remove("hidden"))
}

async function datLich() {
    if (!form.checkValidity())
        return
    let date = document.getElementById("ngayDatLich").value
    const res = await fetch('/api/datlich', {
        method: 'POST',
        body: JSON.stringify({
            'date': date,
            'patient_id': sessionStorage.getItem("patient_id")
        }),
        headers: {
            'Content-Type': 'application/json'
        }
    })
    const data = await res.json()
    sessionStorage.removeItem("patient_id")
    const isDatLich = document.querySelectorAll(".isDatLich")
    isDatLich.forEach(e => e.classList.add("hidden"))
    document.getElementById("nam").disabled = false;
    document.getElementById("nu").disabled = false;
    document.getElementById("Ten").readOnly = false;
    document.getElementById("phone1").readOnly = false;
    document.getElementById("ngaySinh").readOnly = false;
    document.getElementById("thembn").disabled = false
    resetForm()
    if (data.success)
        alert(data.success)
    else alert(data.error)
}

//endregion
// region Danh sách khám
const tableBody = document.getElementById('patient-table-body');
const patientList = document.getElementById('patient-list');


    document.getElementById('form-select-date').addEventListener('submit', async function (e) {
        e.preventDefault();
        const selectedDate = document.getElementById('selectDate').value;
        // Fetch danh sách bệnh nhân
        const res = await
            fetch(`/api/patients?date=${selectedDate}`)
        const data = await res.json()
        sessionStorage.setItem("currentList", JSON.stringify(data))
        tableBody.innerHTML = '';
        if (data.patients.length > 0) {
            patientList.style.display = 'block';
            data.patients.forEach((patient, index) => {
                const row = `
                            <tr itemid="patient-${patient.id}">
                                <td>${index + 1}</td>
                                <td><input type="text" id="name-${patient.id}" class="text-input" value="${patient.name}" readonly></td>
                                <td><input type="date" class="text-input" id="birthday-${patient.id}" name="ngaySinh" value="${patient.birthday}" readonly disabled>
                                </td>
                                <td><input type="text" id="sdt-${patient.id}" class="text-input" value="${patient.sdt}" readonly></td>
                                <td><select id="gender-${patient.id}" disabled>
                                        <option value="nam" ${patient.gender === 'nam' ? 'selected' : ''}>Nam</option>
                                        <option value="nữ" ${patient.gender === 'nữ' ? 'selected' : ''}>Nữ</option>
                                </td>
                                <td>
                                <button class="btn btn-secondary hidden"  id="cancel-${patient.id}">Hủy</button>
                                <button class="btn btn-sm btn-warning" id="btn-edit-${patient.id}" onclick="editPatient(${patient.id})">Sửa</button>
                                <button class="btn btn-sm btn-danger" onclick="deletePatient(${patient.id})">Xóa</button>
                            </td>
                            </tr>`;
                tableBody.insertAdjacentHTML('beforeend', row);
            });
        } else {
            patientList.style.display = 'none';
            alert('Không có bệnh nhân nào chưa xác nhận cho ngày này.');
        }

    });


async function confirmDay() {
    var isconfirm = confirm("Bạn muốn xác nhận toàn bộ lịch khám")
    if (isconfirm) {
        const selectedDate = document.getElementById('selectDate').value;
        // Xác nhận toàn bộ danh sách của ngày
        const res = await fetch(`/api/confirm-day?date=${selectedDate}`, {method: 'POST'})
        const data = await res.json()
        if (data.success) {
            alert('Đã xác nhận toàn bộ danh sách khám ngày ' + selectedDate);
            document.getElementById('form-select-date').submit(); // Làm mới giao diện
            const toast = document.createElement('div');
            toast.classList.add('alert', 'alert-success');
            toast.textContent = 'Danh sách khám ngày ' + selectedDate + ' đã được xác nhận.';
            document.body.appendChild(toast);
        }
    } else alert("Hủy xác nhận")
}

async function editPatient(id) {
    // alert('Chức năng sửa bệnh nhân (ID: ' + id + ') chưa được triển khai.');
    const btn = document.getElementById(`btn-edit-${id}`)
    const input = document.querySelectorAll(`tr[itemid="patient-${id}"] .text-input`)

    const btnCancel = document.getElementById(`cancel-${id}`)
    const name = document.getElementById(`name-${id}`)
    const birthday = document.getElementById(`birthday-${id}`)
    const sdt = document.getElementById(`sdt-${id}`)
    const gender = document.getElementById(`gender-${id}`)

    const tempData = {
        'id': id,
        'name': name.value,
        'birthday': birthday.value,
        'sdt': sdt.value,
        'gender': gender.value,
    }
    if (name.readOnly) {
        for (const i of input) {
            i.readOnly = false
            gender.disabled = false;
            birthday.disabled = false;
        }
        btnCancel.classList.remove("hidden")
        btn.innerText = "Xong"
    } else {
        for (const i of input) {
            i.readOnly = true
            gender.disabled = true;
            birthday.disabled = true;


        }
        btnCancel.classList.add("hidden")
        btn.innerText = "Sửa"
        const data = {
            'id': id,
            'name': name.value,
            'birthday': birthday.value,
            'sdt': sdt.value,
            'gender': gender.value,
        }
        if (confirm('Bạn có chắc muốn sửa đổi bệnh nhân này?')) {
            const res = await fetch(`/api/patient/${id}`, {
                    method: 'PUT',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(data)
                }
            )
            const dataRes = res.json()
        }
    }
    btnCancel.addEventListener('click', () => {
        name.value = tempData['name'];
        birthday.value = tempData['birthday'];
        sdt.value = tempData['sdt'];
        gender.value = tempData['gender']
        btnCancel.classList.add("hidden")
        for (const i of input) {
            i.readOnly = true
            gender.disabled = true;
            birthday.disabled = true;

        }
        btnCancel.classList.add("hidden")
        btn.innerText = "Sửa"
    })


}

async function deletePatient(id) {
    if (confirm('Bạn có chắc muốn xóa bệnh nhân này?')) {
        const res = await fetch(`/api/patient/${id}`, {
                method: 'DELETE',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({'appointment_id': JSON.parse(sessionStorage.getItem("currentList")).appointment_id})
            }
        )
        const data = await res.json()
        alert(data.success);
        tableBody.remove(document.querySelector(`#patient-${id}`))
    }
}

//endregion
