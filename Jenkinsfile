@Library('visenze-lib')_

PROJECTS = [
  'gateway',
  'manager',
  'service',
  'worker'
]

pipeline {
  // choose a suitable agent to build
  agent {
    label 'build'
  }

  options {
    timestamps()
  }

  parameters {
    string(name: 'DOCKER_REGISTRY', defaultValue: '', description: 'leave empty to use dockerhub as registry')
    string(name: 'DOCKER_REGISTRY_CREDENTIAL', defaultValue: 'docker-hub-credential',
        description: 'The credential ID stored in Jenkins to pull/push to docker registry')
    string(name: 'AWS_MAVEN_CREDENTIALS_ID', defaultValue: 'visenze-test-maven-repo')
  }

  tools {
    maven '3.6.3' // enable maven
  }

  stages {
    stage('Checkout') {
      steps {
        // checkout the code from scm (github)
        checkout scm
      }
    }

    stage('Perform Lambda testing') {
      when {
        expression {
          return doLambdacodeTest(env.BRANCH_NAME)
        }
      }
      steps {
        scrips {
          dir('bridge-lambda') {
            lsal = sh (
                script: 'ls',
                returnStdout: true
            ).trim()
            echo "folder info: ${lsal}"
          }
        }
      }
    }
  }
}



// Get commit sha
def getCommit() {
  return sh(
    script: "(cd '${WORKSPACE}'; git rev-parse HEAD)", returnStdout: true
  ).trim()
}

def getVersion() {
  // read version from pom
  return readMavenPom(file: 'pom.xml').properties.revision
}

// Get snapshot version
def genSnapShotVersion(version) {
  def suffix = "-SNAPSHOT"
    if (!version.endsWith(suffix)) {
      return version + suffix
    }
    return version
}

// Get Release version
def genReleaseVersion(version) {
  def suffix = "-SNAPSHOT"
  if (version.endsWith(suffix)) {
    return version.substring(0, version.length() - suffix.length())
  }
  return version
}

def genDockerTags(branch, commit, version=null, buildNumber=null) {
  def tags = []
  def shortCommit = commit.substring(0, 9)
  tags.add(branch.replaceAll("/", "_"))
  tags.add("${branch.replaceAll("/", "_")}-${shortCommit}")
  //if(branch == 'production') {
  //  assert version !=null
  //  tags.add("${version}")
  //} else {
  //  assert version != null && buildNumber != null
  //  tags.add("${version}.${buildNumber}-${shortCommit}")
  //}
  return tags
}

def isPullRequest(branch) {
  return branch.startsWith('PR')
}

def doLambdacodeTest(branch) {
  return branch == "feature/ES-2397/lambda"
}

def doBuildAndTest(branch) {
  return branch.startsWith('PR') || branch == 'staging' || branch == 'production'
}

def isProdRelease(branch) {
  return env.BRANCH_NAME == "production"
}

def dockerBuild(proj, tag, path) {
  docker.withRegistry(params.DOCKER_REGISTRY, params.DOCKER_REGISTRY_CREDENTIAL) {
    sh "docker build -t visenze/bridge-${proj}:${tag} -f docker/Dockerfile-${proj} ${path}"
  }
}

def dockerPush(proj, localTag, tags) {
  docker.withRegistry(params.DOCKER_REGISTRY, params.DOCKER_REGISTRY_CREDENTIAL) {
    def image = docker.image("visenze/bridge-${proj}:${localTag}")
    tags.each {
      retry(2) {
        image.push(it)
      }
    }
  }
}
