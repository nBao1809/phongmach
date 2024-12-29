// region  dat lich
const form = document.querySelector("form")
const resultContainer = document.getElementById("resultContainer");
const newPatientContainer = document.getElementById("newPatientContainer");

async function searchPatient() {
    const phone = document.getElementById("phone").value;
    try {
        const res = await fetch(`/datlich/${phone}`);
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
    document.getElementById("namSinh").value = birthYear;
    // Đặt giới tính vào radio button
    if (gender === "nam") {
        document.getElementById("nam").checked = true;
    } else if (gender === "nữ") {
        document.getElementById("nu").checked = true;
    }

    // Chuyển các ô nhập liệu thành readonly
    document.getElementById("Ten").readOnly = true;
    document.getElementById("phone1").readOnly = true;
    document.getElementById("namSinh").readOnly = true;
    // Khóa radio button (không cho thay đổi giới tính)
    document.getElementById("nam").disabled = true;
    document.getElementById("nu").disabled = true;
    document.getElementById("thembn").disabled = true

    // Hiển thị form mới (nếu cần)
    newPatientContainer.classList.remove("hidden");
}


function resetSearch() {
    sessionStorage.removeItem("patient_id")
    document.getElementById("nam").disabled = false;
    document.getElementById("nu").disabled = false;
    document.getElementById("Ten").readOnly = false;
    document.getElementById("phone1").readOnly = false;
    document.getElementById("namSinh").readOnly = false;
    document.getElementById("thembn").disabled = false
    form.reset();
}

function resetForm() {
    resetSearch();
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
    console.log(data)
    alert("Đã đặt lịch thành công")
}

function addPatient() {
    const patientData = {
        name: document.getElementById('Ten').value,
        phone: document.getElementById('phone1').value,
        birthYear: document.getElementById('namSinh').value,
        gender: document.querySelector('input[name="gioiTinh"]:checked').value,
    };

    fetch('/add_patient', {
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
                document.getElementById("namSinh").readOnly = true;
                // Khóa radio button (không cho thay đổi giới tính)
                document.getElementById("nam").disabled = true;
                document.getElementById("nu").disabled = true;
            }
            alert(data.message);

        })
        .catch(error => {
            console.error('Lỗi khi fetch:', error);
            alert('Có lỗi xảy ra khi thêm bệnh nhân.');
        });
}
//endregion