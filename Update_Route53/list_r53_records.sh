#!/bin/bash 


#########################
### Variable Section
#########################

hosted_zone_id="Z3TT3O182UQECJ"
target_zone_name="tobe.asia"

target_record_name="home"

record_json_file_path="/tmp/r53_${target_record_name}-${target_zone_name}_record.json"

n_date=`date +%Y%m5d-%H%M%S`

#########################
### Function Section 
#########################

function get_g_ips () {
	global_ip=`curl ipconfig.io`
	echo ${global_ip}

}

function get_r53_records () {
aws \
	route53 \
	list-resource-record-sets \
	--hosted-zone-id "${hosted_zone_id}" \
	--query "ResourceRecordSets[?Name == \`${target_record_name}.${target_zone_name}.\`].[ResourceRecords]" \
	--profile=tobe-private-master \
	--output text


}

function update_r53_records () {
aws \
	route53 \
	change-resource-record-sets \
	--hosted-zone-id "${hosted_zone_id}" \
	--change-batch file://${record_json_file_path} \
	--profile=tobe-private-master \
	--output text


}


function create_r53_record_json () {

cat << _EOF_
{
  "Comment" : "Change at ${n_date}",
  "Changes" : [
        {
      "Action" : "UPSERT",
            "ResourceRecordSet" : {
            "Name" : "${target_record_name}.${target_zone_name}",
            "Type" : "A",
            "TTL" : 300,
            "ResourceRecords" : [
              {
                  "Value": "${local_g_ip}"
              }
            ]
            }
      }
   ]
}
_EOF_
}



function main () {

local_g_ip=`get_g_ips`
r53_record_ip=`get_r53_records`

echo "## Local ###"  ${local_g_ip}
echo "## DNS Record ###"  ${r53_record_ip}

if [ ${local_g_ip} = ${r53_record_ip} ]; then

	echo "${target_record_name}.${target_zone_name} record is corrected"
else
	echo "Make ${target_record_name}.${target_zone_name} record JSON"

	create_r53_record_json |jq . >| ${record_json_file_path}

	echo "Create JSON Finished!"
	echo "##---------------------##"
	echo "UPDATE DNS Records"

	update_r53_records

fi

}


#########################
### Main Section 
#########################

main
