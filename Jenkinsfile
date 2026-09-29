pipeline {
    agent any
   
    stages {

        stage('Checkout') {
            steps {
                checkout scm

            }
        }

        stage('Environment Check') {
            steps {
                sh '''
                    echo "Jenkins user:"
                    whoami

                    echo "Python:"
                    python3 --version

                    echo "Git:"
                    git --version
                '''
            }
        }

        stage('Install Dependencies') {
            steps {
                sh '''
                    python3 -m venv .jenkins-venv
                    . .jenkins-venv/bin/activate
                    pip install --upgrade pip
                    pip install -r requirements.txt
                '''
            }
        }

        stage('Syntax Test') {
            steps {
                sh '''
                    . .jenkins-venv/bin/activate
                    python -m py_compile api.py
                '''
            }
        }

        stage('Deploy') {
            steps {
                sh '''
                    sudo /usr/local/bin/deploy-my-api
                '''
            }
        }         

        stage('Health Check') {
            steps {
                sh '''
                    curl --fail http://127.0.0.1:8000/health
                '''
            }
        }
    }

    post {
        success {
            echo 'Jenkins deployment completed successfully.'
        }

        failure {
            echo 'Jenkins pipeline failed.'
        }
    }
}
