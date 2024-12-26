const form = document.querySelector("form")
const resultContainer = document.getElementById("resultContainer");
const newPatientContainer = document.getElementById("newPatientContainer");

async function searchPatient() {
    const phone = document.getElementById("phone").value;
    const res = await fetch(`/datlich/${phone}`)
    const patient = await res.json()
    console.log(patient)
    // Giả lập dữ liệu bệnh nhân


    if (patient) {
        // Hiển thị thông tin bệnh nhân
        document.getElementById("resultName").innerText = patient["name"];
        document.getElementById("resultBirthYear").innerText = patient["birthday"];
        document.getElementById("resultGender").innerText = patient["gender"];
        document.getElementById("resultPhone").innerText = patient["sdt"];

        resultContainer.classList.remove("hidden");
    } else {
        // Không tìm thấy bệnh nhân
        alert("Không tìm thấy bệnh nhân. Vui lòng nhập thông tin mới.");
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
    // Hiển thị form mới (nếu cần)
    newPatientContainer.classList.remove("hidden");
}


function resetSearch() {
    document.getElementById("nam").disabled = false;
    document.getElementById("nu").disabled = false;
    document.getElementById("Ten").readOnly = false;
    document.getElementById("phone1").readOnly = false;
    document.getElementById("namSinh").readOnly = false;
    form.reset();
}

function resetForm() {
    resetSearch();
}

async function datLich() {
    let date = document.getElementById("ngayDatLich")
    const res = await fetch('/api/datlich', {
        method: 'POST',
        body: JSON.stringify({
            'date': date
        }),
        headers: {
            'Content-Type': 'application/json'
        }
    })
    const data = await res.json()
//     TODO Thêm thông báo thêm thành công
}