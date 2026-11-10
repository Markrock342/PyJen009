// PyJen009 — Build, Test, Deploy อัตโนมัติ
// Jenkins เช็ก GitHub ทุก 1 นาที เจอ commit ใหม่จะรัน pipeline นี้เอง
pipeline {
    agent any

    triggers {
        pollSCM('* * * * *')
    }

    options {
        buildDiscarder(logRotator(numToKeepStr: '20'))
        disableConcurrentBuilds()
    }

    environment {
        PORT = '8009'
    }

    stages {
        stage('Build') {
            steps {
                sh 'python3 --version'
                // ตรวจว่าโค้ดทุกไฟล์คอมไพล์ผ่าน (ไม่มี syntax error)
                sh 'python3 -m py_compile calculator.py app.py tests/*.py'
                sh 'python3 calculator.py 2 3'
            }
        }

        stage('Test') {
            steps {
                sh 'python3 -m unittest discover -s tests -t . -v'
            }
        }

        stage('Deploy') {
            steps {
                // ไม่ให้ Jenkins ปิดเว็บที่รันค้างไว้หลัง build จบ
                withEnv(['JENKINS_NODE_COOKIE=dontKillMe', 'BUILD_ID=dontKillMe']) {
                    sh 'chmod +x scripts/deploy.sh'
                    sh './scripts/deploy.sh'
                }
            }
        }
    }

    post {
        success {
            echo "Build, Test, Deploy สำเร็จ — เปิด http://127.0.0.1:${PORT}"
        }
        failure {
            echo 'Pipeline ไม่ผ่าน ดู log ของ stage ที่เป็นสีแดง'
        }
    }
}
