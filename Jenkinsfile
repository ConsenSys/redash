node {
    def baseImageName = "photic-docker-node"
    def targetImageName = 'photic-docker-analytics'

    def tagPrefix;
    switch ("${env.sha1}") {
        case ~/^.*master$/: tagPrefix = 'it'; break
        case ~/^.*\/.*$/: tagPrefix = 'pr'; break
        default: tagPrefix = "br-${env.sha1}"; break
    }

    docker.withRegistry("https://${env.DOCKER_REGISTRY}", "${env.DOCKER_CREDENTIALS}") { 
        stage ('Checkout Repository') {
            checkout scm 
        }

        stage ("Build Dashboard Image") {
            customImage = docker.build("${targetImageName}:${tagPrefix}-${currentBuild.startTimeInMillis}", "--build-arg DOCKER_REGISTRY=${env.DOCKER_REGISTRY} .");
        }

        if ("$tagPrefix" != "pr") { 
            stage ("Push Dashboard Image") {
                customImage.push(); 
                customImage.push("latest");
            }
        }
    }
}