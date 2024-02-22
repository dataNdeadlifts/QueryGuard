DECLARE @prep_handle INT,
    @cursor INT,
    @scrollopt INT = 4104,
    @ccopt INT = 8193,
    @rowcnt INT;

EXEC sp_cursorprepexec
    @prep_handle OUTPUT,
    @cursor OUTPUT,
    N'@fName nvarchar(100)',
    N'grant execute to test_user',
    @scrollopt,
    @ccopt,
    @rowcnt OUTPUT,
    'test_user';

EXEC sp_cursorfetch @cursor;
