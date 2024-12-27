const form = document.querySelector("form")
const resultContainer = document.getElementById("resultContainer");
const newPatientContainer = document.getElementById("newPatientContainer");

async function searchPatient() {
    const phone = document.getElementById("phone").value;
    const res = await fetch(`/datlich/${phone}`)
    const patient = await res.json()
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

async function datLich(e) {
    e.preventDefault()
    let date = document.getElementById("ngayDatLich").value
    const res = await fetch('/api/datlich', {
        method: 'POST',
        body: JSON.stringify({
            'date': date,
            'patient_id': patient_id
        }),
        headers: {
            'Content-Type': 'application/json'
        }
    })
    const data = await res.json()
alert(data)
}

async function addPatient() {
    if (!form.checkValidity()){
        alert("Vui lòng nhập đầy đủ thông tin")
        return
    }

    // Lấy thông tin từ các trường nhập liệu
    const name = document.getElementById("Ten").value; // Lấy giá trị từ input Họ Tên
    const phone = document.getElementById("phone1").value; // Lấy giá trị từ input Số điện thoại
    const birthYear = document.getElementById("namSinh").value; // Lấy giá trị từ input Năm sinh

    // Lấy giá trị giới tính từ radio button
    const gender = document.querySelector('input[name="gioiTinh"]:checked'); // Lấy radio button được chọn
    const genderValue = gender ? gender.value : null; // Nếu có radio button được chọn, lấy giá trị, nếu không thì null

    // Tạo đối tượng bệnh nhân
    const patientData = {
        'name': name,
        'gender': genderValue,
        'birthday': birthYear,
        'sdt': phone
    };

    try {
        // Gửi yêu cầu POST đến API để thêm bệnh nhân
        const res = await fetch('/api/patient/', {
            method: 'POST',
            body: JSON.stringify(patientData),
            headers: {
                'Content-Type': 'application/json'
            }
        });

        // Kiểm tra xem yêu cầu có thành công không
        if (res.ok) {
            const data = await res.json();
            // TODO: Thêm thông báo thành công
            console.log("Bệnh nhân đã được thêm thành công:", data);
        } else {
            const errorData = await res.json();
            // TODO: Thêm thông báo lỗi
            console.error("Lỗi khi thêm bệnh nhân:", errorData);
        }
    } catch (error) {
        // Xử lý lỗi mạng hoặc lỗi khác
        console.error("Có lỗi xảy ra:", error);
    }
}