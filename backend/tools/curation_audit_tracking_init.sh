source tools/util_startup.sh

function curation_audit_tracking_init {
    startup_log "CURATION_AUDIT_TRACKING" "BEGIN"
    python manage.py curation_audit_tracking --init
    python manage.py curation_audit_tracking --disable
    local result=$?
    startup_log "CURATION_AUDIT_TRACKING" "END"
    return $result
}
