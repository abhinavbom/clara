#!/usr/bin/env bash
# 06/23/2019 - Adding new feature that creates Yara scanning lambda fucntion
#author: Abhinav Singh

# Upside Travel, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

lambda_output_file=/opt/app/build/lambda.zip

set -e

yum update -y
yum install -y cpio python3-pip yum-utils zip
yum -y install gcc openssl-devel bzip2-devel libffi-devel
yum install -y https://dl.fedoraproject.org/pub/epel/epel-release-latest-7.noarch.rpm
yum install https://www.rpmfind.net/linux/epel/7/x86_64/Packages/y/yara-3.8.1-1.el7.x86_64.rpm
yum install -y python3-devel.x86_64

pip3 install --no-cache-dir virtualenv


virtualenv env
. env/bin/activate
pip3 install --no-cache-dir -r requirements.txt

pushd /tmp
yumdownloader -x \*i686 --archlist=x86_64 clamav clamav-lib clamav-update json-c pcre2 yara
rpm2cpio clamav-0*.rpm | cpio -idmv
rpm2cpio clamav-lib*.rpm | cpio -idmv
rpm2cpio clamav-update*.rpm | cpio -idmv
rpm2cpio json-c*.rpm | cpio -idmv
rpm2cpio pcre*.rpm | cpio -idmv
rpm2cpio yara*.rpm | cpio -idmv
popd
mkdir -p bin
cp /tmp/usr/bin/clamscan /tmp/usr/bin/freshclam /tmp/usr/bin/yara /tmp/usr/bin/yarac /tmp/usr/lib64/* bin/.
echo "DatabaseMirror database.clamav.net" > bin/freshclam.conf
mkdir -p build
zip -r9 $lambda_output_file *.py bin
cd env/lib/python3.7/site-packages
zip -r9 $lambda_output_file *