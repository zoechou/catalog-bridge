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

  stages {
  stage('Checkout') {
    steps {
      // checkout the code from scm (github)
      checkout scm
    }
  }

  stage('Lambda archiving') {
    steps {
      script {
        dir('bridge-lambda') {
          def s3_bucket = 'visenze-lambda-code-bucket-test'
          def aws_cred_id  = 'aws-staging'
          def deploy_workspace = 'test-staging'

          if(env.BRANCH_NAME == 'production'){
            s3_bucket = 'online-sg-enterprise-lambda-code'
            aws_cred_id = 'aws-online-lambda-cd'
            deploy_workspace = 'prod-commerce-connector'
          }

          def function_list = sh(script:"ls", returnStdout: true)

          for(lambda_function_name in function_list.split('\n')){
            def code_path = "${lambda_function_name}/src"

            try {
              lambda.codeArchive(code_path,
                              lambda_function_name,
                              'v1',
                              'Enterprise',
                              'commerce',
                              'commerce',
                              s3_bucket,
                              'us-west-2',
                              aws_cred_id
              )
            }
            catch(all) {
                print(all)
            }
          }
        }
      }
    }
  }

  stage('Lambda deploy') {
    steps {
      scripts {
        build job: 'sre-update-infrastructure', parameters: [string(name: 'INFRASTRUCTURE', value: 'aws-lambda'), string(name: 'INFRA_WORKSPACE', value: "${deploy_workspace}"), string(name: 'CLOUD_FORM_BRANCH', value: 'feature/DOS-513'), string(name: 'AGENT_LABEL', value: 'pod-od'), string(name: 'VISENZE_LIB_BRANCH', value: 'master')]
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
