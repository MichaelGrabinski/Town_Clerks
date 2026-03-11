from django.db import models


class ActivityLog(models.Model):
    """Audit log for site activity (requests + explicit actions).

    Stored in the app's default DB.
    """

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    # Who
    user = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='town_clerks_activity_logs',
    )
    username = models.CharField(max_length=150, blank=True, default='')

    # What
    event_type = models.CharField(max_length=50, db_index=True)  # request / search / view / export / etc
    action = models.CharField(max_length=200, blank=True, default='')

    # Where
    path = models.CharField(max_length=500, blank=True, default='')
    method = models.CharField(max_length=10, blank=True, default='')
    status_code = models.IntegerField(blank=True, null=True)

    # Request metadata
    ip_address = models.CharField(max_length=64, blank=True, default='')
    user_agent = models.TextField(blank=True, default='')
    referer = models.CharField(max_length=500, blank=True, default='')

    # Data
    query_string = models.TextField(blank=True, default='')
    extra = models.JSONField(blank=True, null=True)

    class Meta:
        managed = True
        ordering = ['-created_at']

    def __str__(self):
        u = self.username or (self.user.username if self.user_id else 'anonymous')
        return f"{self.created_at:%Y-%m-%d %H:%M:%S} {u} {self.event_type} {self.path}"

# --- New App Models (Managed by Django in 'Cler' DB) ---

class VetRecord(models.Model):
    # This stores the JSON blob from new ingestions if needed
    data = models.JSONField()
    imported_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"VetRecord {self.id}"

    class Meta:
        managed = True

class TransmitelReport(models.Model):
    filename = models.CharField(max_length=255)
    data = models.JSONField()
    imported_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.filename

    class Meta:
        managed = True


class TransmittalReport(models.Model):
    """Clerk-keyed transmittal report with line items stored as JSON."""
    report_date = models.DateField()
    prepared_by = models.CharField(max_length=150)
    notes = models.TextField(blank=True, default='')
    line_items = models.JSONField(default=list)          # [{account, description, checks, cash, total}, ...]
    grand_total_checks = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    grand_total_cash = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    grand_total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = True
        ordering = ['-created_at']

    def __str__(self):
        return f"Transmittal {self.report_date} — {self.prepared_by}"


# --- Legacy Models from 'Marriage' DB ---

class Allmarriages(models.Model):
    marriage_id = models.IntegerField(db_column='Marriage_ID', primary_key=True)
    groomfirstname = models.CharField(db_column='GroomFirstName', max_length=50, blank=True, null=True)
    groomlastname = models.CharField(db_column='GroomLastName', max_length=50, blank=True, null=True)
    bridefirstname = models.CharField(db_column='BrideFirstName', max_length=50, blank=True, null=True)
    bridelastname = models.CharField(db_column='BrideLastName', max_length=50, blank=True, null=True)
    dateofmarriage = models.DateTimeField(db_column='DateofMarriage', blank=True, null=True)
    town_marriage = models.CharField(db_column='Town_marriage', max_length=25, blank=True, null=True)
    
    class Meta:
        managed = False
        db_table = 'AllMarriages'
    app_label = 'clerks_legacy'

class Marriagesfrombooks(models.Model):
    bookmar_id = models.IntegerField(db_column='BookMar_ID', primary_key=True)
    groom_lastname = models.CharField(db_column='Groom _LastName', max_length=50, blank=True, null=True)
    groom_firsttname = models.CharField(db_column='Groom _FirsttName', max_length=50, blank=True, null=True)
    bride_lastname = models.CharField(db_column='Bride_LastName', max_length=50, blank=True, null=True)
    bride_firstname = models.CharField(db_column='Bride_FirstName', max_length=50, blank=True, null=True)
    date_of_marriage = models.DateTimeField(db_column='Date_Of_ Marriage', blank=True, null=True)
    
    class Meta:
        managed = False
        db_table = 'MarriagesfromBooks'
    app_label = 'clerks_legacy'

class Marriagelicense(models.Model):
    marriage_id = models.CharField(db_column='Marriage_ID', primary_key=True, max_length=255)
    groomfirstname = models.CharField(db_column='GroomFirstName', max_length=255, blank=True, null=True)
    groommiddlename = models.CharField(db_column='GroomMiddleName', max_length=255, blank=True, null=True)
    groomlastname = models.CharField(db_column='GroomLastName', max_length=255, blank=True, null=True)
    bridefirstname = models.CharField(db_column='BrideFirstName', max_length=255, blank=True, null=True)
    bridemiddlename = models.CharField(db_column='BrideMiddleName', max_length=255, blank=True, null=True)
    bridelastname = models.CharField(db_column='BrideLastName', max_length=255, blank=True, null=True)
    town_marriage = models.CharField(db_column='Town_marriage', max_length=255, blank=True, null=True)
    date_issued = models.CharField(db_column='Date_Issued', max_length=255, blank=True, null=True)
    dateofmarriage = models.CharField(db_column='DateofMarriage', max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = '[stg].[MarriageLicense]'
    app_label = 'clerks_legacy'

class Civilunion(models.Model):
    union_id = models.IntegerField(db_column='Union_ID', primary_key=True)
    party1_firstname = models.CharField(db_column='Party1_FirstName', max_length=50, blank=True, null=True)
    party1lastname = models.CharField(db_column='Party1LastName', max_length=50, blank=True, null=True)
    party2firstname = models.CharField(db_column='Party2FirstName', max_length=50, blank=True, null=True)
    party2lastname = models.CharField(db_column='Party2LastName', max_length=50, blank=True, null=True)
    dateofunion = models.DateTimeField(db_column='DateofUnion', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'CivilUnion'
    app_label = 'clerks_legacy'


# --- Legacy Models from 'Vets' DB ---

class Vet(models.Model):
    vet_id = models.CharField(db_column='Vet_ID', primary_key=True, max_length=255)
    lname = models.CharField(db_column='Lname', max_length=255, blank=True, null=True)
    fname = models.CharField(db_column='FName', max_length=255, blank=True, null=True)
    middlename = models.CharField(db_column='MiddleName', max_length=255, blank=True, null=True)
    stnum = models.CharField(db_column='StNum', max_length=255, blank=True, null=True)
    town = models.CharField(db_column='Town', max_length=255, blank=True, null=True)
    st = models.CharField(db_column='ST', max_length=255, blank=True, null=True)
    streetname = models.CharField(db_column='StreetName', max_length=255, blank=True, null=True)
    unit = models.CharField(db_column='Unit', max_length=255, blank=True, null=True)
    volume = models.CharField(db_column='Volume', max_length=255, blank=True, null=True)
    page = models.CharField(db_column='Page', max_length=255, blank=True, null=True)
    enlistment_date = models.CharField(db_column='Enlistment_Date', max_length=255, blank=True, null=True)
    discharge_date = models.CharField(db_column='Discharge_Date', max_length=255, blank=True, null=True)
    birth_date = models.CharField(db_column='Birth_Date', max_length=255, blank=True, null=True)
    recording_date = models.CharField(db_column='Recording_Date', max_length=255, blank=True, null=True)
    branch = models.CharField(db_column='Branch', max_length=255, blank=True, null=True)
    spousepartner = models.CharField(db_column='SpousePartner', max_length=255, blank=True, null=True)

    @property
    def branch_name(self):
        """Human readable branch name via stg.refBranch (e.g. '4' -> 'AIR FORCE')."""
        if not self.branch:
            return ''
        b = (self.branch or '').strip()
        # If value is already a name, just show it.
        if not b.isdigit():
            return b
        try:
            return Refbranch.objects.using('vets').get(branchid=b).branch or b
        except Exception:
            return b

    class Meta:
        managed = False
        db_table = '[stg].[vet]'
    app_label = 'clerks_legacy'


class Refbranch(models.Model):
    branchid = models.CharField(db_column='BranchID', primary_key=True, max_length=255)
    branch = models.CharField(db_column='Branch', max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = '[stg].[refBranch]'
    app_label = 'clerks_legacy'

# --- Legacy Models from 'Clerk_Transmittal' DB ---

class Transactions(models.Model):
    transaction_id = models.CharField(db_column='Transaction_ID', primary_key=True, max_length=255)
    transactionnumber = models.CharField(db_column='TransactionNumber', max_length=255, blank=True, null=True)
    transactiondate = models.CharField(db_column='TransactionDate', max_length=255, blank=True, null=True)
    entered_by = models.CharField(db_column='Entered BY', max_length=255, blank=True, null=True)
    accountid = models.CharField(db_column='AccountID', max_length=255, blank=True, null=True)
    depositamount = models.CharField(db_column='DepositAmount', max_length=255, blank=True, null=True)
    description = models.CharField(db_column='Description', max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = '[stg].[Transactions]'
    app_label = 'clerks_legacy'

class Accounts(models.Model):
    accountid = models.IntegerField(db_column='AccountID', primary_key=True)
    accountname = models.CharField(db_column='AccountName', max_length=50, blank=True, null=True)
    accountnumber = models.CharField(db_column='AccountNumber', max_length=50, blank=True, null=True)
    
    class Meta:
        managed = False
        db_table = '[stg].[Accounts]'
    app_label = 'clerks_legacy'

# --- Legacy Models from 'Vitals' DB ---

class Deaths(models.Model):
    id = models.CharField(db_column='ID', primary_key=True, max_length=255)
    entry_date = models.CharField(db_column='Entry_Date', max_length=255, blank=True, null=True)
    date_of_death = models.CharField(db_column='Date Of Death', max_length=255, blank=True, null=True)
    lastname = models.CharField(db_column='Lastname', max_length=255, blank=True, null=True)
    first_name = models.CharField(db_column='First Name', max_length=255, blank=True, null=True)
    middlename = models.CharField(db_column='MiddleName', max_length=255, blank=True, null=True)
    street_address = models.CharField(db_column='Street Address', max_length=255, blank=True, null=True)
    date_of_birth = models.CharField(db_column='Date Of Birth', max_length=255, blank=True, null=True)
    page_number = models.CharField(db_column='Page Number', max_length=255, blank=True, null=True)
    non_eh = models.CharField(db_column='Non_EH', max_length=255, blank=True, null=True)
    suffix = models.CharField(db_column='Suffix', max_length=255, blank=True, null=True)
    unit = models.CharField(db_column='unit', max_length=255, blank=True, null=True)
    town = models.CharField(db_column='Town', max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = '[stg].[Deaths]'
    app_label = 'clerks_legacy'
