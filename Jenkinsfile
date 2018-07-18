node {
    def baseImageName = "photic-docker-node"
    def targetImageName = 'photic-docker-analytics'

    def tagPrefix;
    switch ("${env.sha1}") {
        case ~/^.*photic$/: tagPrefix = 'dev'; break
        case ~/^.*\/.*$/: tagPrefix = 'pr'; break
        default: tagPrefix = "br-${env.sha1}"; break
    }

    docker.withRegistry("https://${env.DOCKER_REGISTRY}", "${env.DOCKER_CREDENTIALS}") { 
        stage ('Checkout Repository') {
            checkout scm 
        }

        stage ("Build Workers Image") {
            customWorkersImage = docker.build("${targetImageName}workers:${tagPrefix}-${currentBuild.startTimeInMillis}", "--build-arg DOCKER_REGISTRY=${env.DOCKER_REGISTRY} .");
        }

        stage ("Build Dashboard Image") {
            customDashboardImage = docker.build("${targetImageName}dashboard:${tagPrefix}-${currentBuild.startTimeInMillis}", "--build-arg DOCKER_REGISTRY=${env.DOCKER_REGISTRY} .");
        }

        if ("$tagPrefix" != "pr") {
            stage ("Push Workers Image") {
                customWorkersImage.push(); 
                customWorkersImage.push("latest");
            }

            stage ("Push Dashboard Image") {
                customDashboardImage.push(); 
                customDashboardImage.push("latest");
            }
        }
    }
}